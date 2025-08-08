"""
سرویس‌های مربوط به Scroll Time برای دریافت داده از سازمان بورس
"""
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from django.conf import settings
from price_data_ingestion.models import ScrollTimeRequest
from price_models.models import PriceData, DataImportLog
from data_management.models import AllData as DataManagementAllData

logger = logging.getLogger(__name__)


def convert_shamsi_to_gregorian(shamsi_date_str: str) -> date:
    """
    تبدیل تاریخ شمسی به میلادی (ساده‌سازی شده)
    
    Args:
        shamsi_date_str: تاریخ شمسی به فرمت 1403/05/01
        
    Returns:
        datetime.date object
    """
    try:
        if not shamsi_date_str:
            return datetime.now().date()

        # پاک‌سازی ورودی: حذف نویسه‌های اضافی مانند گیومه فارسی و انگلیسی
        clean_str = shamsi_date_str.strip()
        for ch in ['“', '”', '"', "'"]:
            clean_str = clean_str.replace(ch, '')
        # تبدیل ساده - فعلاً 622 سال کم می‌کنیم
        # در آینده باید از کتابخانه دقیق‌تری استفاده کرد
        parts = clean_str.split('/')
        if len(parts) != 3:
            return datetime.now().date()
        year, month, day = parts
        gregorian_year = int(year) + 621  # تقریبی
        
        # محدود کردن ماه و روز
        gregorian_month = min(int(month), 12)
        gregorian_day = min(int(day), 28)  # برای جلوگیری از خطا
        
        return datetime(gregorian_year, gregorian_month, gregorian_day).date()
        
    except Exception as e:
        logger.warning(f"Error converting shamsi date {shamsi_date_str}: {e}")
        return datetime.now().date()


class ScrollTimeService:
    """سرویس اصلی برای کار با API سازمان بورس"""
    
    BASE_URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList"
    
    # Headers پیش‌فرض برای درخواست - مطابق کد موفق
    DEFAULT_HEADERS = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': 'text/plain, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept-Language': 'fa-IR,fa;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
    
    def fetch_data(self, scroll_request: ScrollTimeRequest) -> Dict[str, Any]:
        """
        دریافت داده از سرور بورس
        
        Args:
            scroll_request: شی درخواست Scroll Time
            
        Returns:
            Dict شامل داده‌های دریافت شده یا خطا
        """
        try:
            # تغییر وضعیت به "در حال پردازش"
            scroll_request.status = 'processing'
            scroll_request.save()
            
            # ایجاد payload
            payload = scroll_request.get_payload()
            
            logger.info(f"Sending request to {self.BASE_URL}")
            logger.info(f"Payload: {payload}")
            
            # بررسی payload قبل از ارسال
            # نکته: در API سازمان بورس، مقدار 0 به معنای "همه" است و معتبر است
            if payload.get('MainCat') is None or payload.get('Cat') is None or payload.get('SubCat') is None:
                error_msg = "اطلاعات دسته‌بندی کامل نیست. لطفاً دسته‌بندی‌ها را کامل کنید."
                logger.error(error_msg)
                
                scroll_request.status = 'failed'
                scroll_request.error_message = error_msg
                scroll_request.save()
                
                return {
                    'success': False,
                    'error': error_msg,
                    'data': None
                }
            
            # ارسال درخواست با timeout بیشتر و retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1}/{max_retries}")
                    
                    response = self.session.post(
                        self.BASE_URL,
                        json=payload,  # استفاده از json به جای data - مطابق کد موفق
                        timeout=30  # timeout افزایش یافته برای شبکه کندتر
                    )
                    
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response headers: {dict(response.headers)}")
                    
                    # بررسی وضعیت پاسخ
                    if response.status_code == 200:
                        break
                    elif response.status_code == 500 and attempt < max_retries - 1:
                        logger.warning(f"Server error on attempt {attempt + 1}, retrying...")
                        continue
                    else:
                        response.raise_for_status()
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                        continue
                    else:
                        raise
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Request error on attempt {attempt + 1}: {e}, retrying...")
                        continue
                    else:
                        raise
            
            # پردازش پاسخ JSON - API IME پاسخ را در فیلد "d" قرار می‌دهد
            response_json = response.json()
            logger.info(f"Raw response JSON: {response_json}")
            
            # استخراج داده‌های اصلی از فیلد "d"
            if 'd' in response_json:
                # داده‌ها در فیلد "d" به صورت JSON string هستند
                data_string = response_json.get('d', '[]')
                logger.info(f"Data string from 'd' field: {data_string[:500]}...")  # نمایش 500 کاراکتر اول
                try:
                    data = json.loads(data_string) if isinstance(data_string, str) else data_string
                except json.JSONDecodeError as decode_error:
                    logger.error(f"JSON decode error: {decode_error}")
                    data = data_string
            else:
                data = response_json
            
            # بررسی اینکه data یک لیست است
            if not isinstance(data, list):
                logger.warning(f"Data is not a list, type: {type(data)}, value: {data}")
                data = []
                
            logger.info(f"Final processed data length: {len(data)}")
            
            # ذخیره داده‌های پاسخ
            scroll_request.response_data = data
            scroll_request.total_records = len(data)
            scroll_request.status = 'preview'
            scroll_request.save()
            
            logger.info(f"Successfully received {len(data)} records")
            
            return {
                'success': True,
                'data': data,
                'total_records': len(data),
                'message': f'دریافت {len(data)} رکورد با موفقیت انجام شد'
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"خطا در ارسال درخواست: {str(e)}"
            
            # اطلاعات تکمیلی برای debug
            debug_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'url': self.BASE_URL,
                'payload': payload,
                'headers': dict(self.session.headers),
                'method': 'POST'
            }
            
            if hasattr(e, 'response') and e.response is not None:
                debug_details['response_status'] = e.response.status_code
                debug_details['response_headers'] = dict(e.response.headers)
                try:
                    debug_details['response_text'] = e.response.text[:1000]  # اول 1000 کاراکتر
                except:
                    debug_details['response_text'] = 'نمی‌توان محتوای پاسخ را خواند'
            
            logger.error(f"Request failed with details: {debug_details}")
            
            scroll_request.status = 'failed'
            scroll_request.error_message = f"{error_msg}\n\nجزئیات: {debug_details}"
            scroll_request.save()
            
            return {
                'success': False,
                'error': error_msg,
                'debug_details': debug_details,
                'data': None
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"خطا در پردازش پاسخ JSON: {str(e)}"
            logger.error(error_msg)
            
            scroll_request.status = 'failed'
            scroll_request.error_message = error_msg
            scroll_request.save()
            
            return {
                'success': False,
                'error': error_msg,
                'data': None
            }
            
        except Exception as e:
            error_msg = f"خطای غیرمنتظره: {str(e)}"
            logger.error(error_msg)
            
            scroll_request.status = 'failed'
            scroll_request.error_message = error_msg
            scroll_request.save()
            
            return {
                'success': False,
                'error': error_msg,
                'data': None
            }
    
    def save_data_to_database(self, scroll_request: ScrollTimeRequest) -> Dict[str, Any]:
        """
        ذخیره داده‌های دریافت شده در پایگاه داده
        
        Args:
            scroll_request: شی درخواست Scroll Time
            
        Returns:
            Dict شامل گزارش عملکرد
        """
        try:
            if not scroll_request.response_data:
                return {
                    'success': False,
                    'error': 'هیچ داده‌ای برای ذخیره وجود ندارد',
                    'stats': {}
                }
            
            # آمار عملکرد
            stats = {
                'total_records': 0,
                'imported_records': 0,
                'updated_records': 0,
                'duplicate_records': 0,
                'error_records': 0,
            }
            
            data_list = scroll_request.response_data
            if not isinstance(data_list, list):
                data_list = [data_list]
            
            stats['total_records'] = len(data_list)
            
            # پردازش هر رکورد
            for record in data_list:
                try:
                    processed = self._process_single_record(record, scroll_request, stats)
                    if processed:
                        stats['imported_records'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing record: {e}")
                    stats['error_records'] += 1
            
            # بروزرسانی وضعیت درخواست
            scroll_request.status = 'completed'
            scroll_request.processed_records = stats['imported_records'] + stats['updated_records']
            scroll_request.save()
            # ایجاد لاگ وارد کردن داده (در صورت خطا آن را نادیده بگیرید)
            try:
                self._create_import_log(scroll_request, stats)
            except Exception as log_exc:
                logger.warning(f"Skipping import log due to error: {log_exc}")
            
            return {
                'success': True,
                'stats': stats,
                'message': f'ذخیره داده‌ها با موفقیت انجام شد. {stats["imported_records"]} رکورد جدید، {stats["updated_records"]} رکورد بروزرسانی شد.'
            }
            
        except Exception as e:
            error_msg = f"خطا در ذخیره داده‌ها: {str(e)}"
            logger.error(error_msg)
            
            scroll_request.status = 'failed'
            scroll_request.error_message = error_msg
            scroll_request.save()
            
            return {
                'success': False,
                'error': error_msg,
                'stats': stats
            }
    
    def _process_single_record(self, record: Dict[str, Any], scroll_request: ScrollTimeRequest, stats: Dict[str, int]) -> bool:
        """
        پردازش یک رکورد منفرد
        
        Args:
            record: رکورد داده
            scroll_request: درخواست اصلی
            stats: آمار عملکرد
            
        Returns:
            True اگر رکورد با موفقیت پردازش شد
        """
        try:
            # استخراج اطلاعات از رکورد واقعی Iran Exchange API
            goods_name = record.get('GoodsName', 'نامشخص')
            symbol = record.get('Symbol', '')
            shamsi_date_str = record.get('date')  # فرمت: 1403/05/01
            
            # تبدیل تاریخ شمسی به میلادی
            price_date = convert_shamsi_to_gregorian(shamsi_date_str)
            
            # بررسی وجود رکورد تکراری براساس commodity_name و price_date
            # (مطابق unique_together در مدل)
            existing_record = PriceData.objects.filter(
                commodity_name=goods_name,
                price_date=price_date
            ).first()
            
            # بررسی وجود رکورد تکراری در AllData نیز
            existing_alldata = DataManagementAllData.objects.filter(
                commodity_name=goods_name,
                transaction_date=shamsi_date_str
            ).first()
            
            if existing_record or existing_alldata:
                stats['duplicate_records'] += 1
                
                # رفتار با داده‌های تکراری
                if scroll_request.duplicate_handling == 'skip':
                    return False
                elif scroll_request.duplicate_handling == 'update':
                    if existing_record:
                        self._update_price_record(existing_record, record)
                    if existing_alldata:
                        self._update_alldata_record(existing_alldata, record, scroll_request)
                    stats['updated_records'] += 1
                    return True
                elif scroll_request.duplicate_handling == 'replace':
                    if existing_record:
                        existing_record.delete()
                    if existing_alldata:
                        existing_alldata.delete()
                    self._create_price_record(record, scroll_request)
                    self._create_alldata_record(record, scroll_request)
                    return True
            else:
                # ایجاد رکوردهای جدید در هر دو جدول
                self._create_price_record(record, scroll_request)
                self._create_alldata_record(record, scroll_request)
                return True
                
        except Exception as e:
            logger.error(f"Error processing single record: {e}")
            logger.error(f"Record data: {record}")
            raise
    
    def _create_price_record(self, record: Dict[str, Any], scroll_request: ScrollTimeRequest) -> PriceData:
        """ایجاد رکورد جدید PriceData براساس ساختار Iran Exchange API"""
        
        # تبدیل تاریخ شمسی به میلادی
        shamsi_date_str = record.get('date', '')  # 1403/05/01
        price_date = convert_shamsi_to_gregorian(shamsi_date_str)
        
        return PriceData.objects.create(
            # اطلاعات اصلی کالا (mapping به field های واقعی PriceData)
            commodity_name=record.get('GoodsName', 'نامشخص')[:100],  # محدود به 100 کاراکتر
            symbol=record.get('Symbol', '')[:50],  # محدود به 50 کاراکتر
            
            # تاریخ
            price_date=price_date,
            
            # اطلاعات قیمت (mapping به field های واقعی)
            final_price=record.get('Price', 0),  # قیمت نهایی
            avg_price=record.get('Price', 0),    # فعلاً از همان Price استفاده می‌کنیم
            lowest_price=record.get('MinPrice', 0),  # کمترین قیمت
            highest_price=record.get('MaxPrice', 0),  # بیشترین قیمت
            
            # اطلاعات حجم و ارزش
            volume=int(record.get('Quantity', 0)) if record.get('Quantity') else None,  # حجم
            value=record.get('TotalPrice', 0),  # ارزش کل
            unit=record.get('Unit', '')[:20],  # واحد - محدود به 20 کاراکتر
            
            # متاداده
            source='scroll_time'
        )
    
    def _update_price_record(self, existing_record: PriceData, new_data: Dict[str, Any]):
        """بروزرسانی رکورد موجود براساس ساختار Iran Exchange API"""
        existing_record.commodity_name = new_data.get('GoodsName', existing_record.commodity_name)[:100]
        existing_record.final_price = new_data.get('Price', existing_record.final_price)
        existing_record.avg_price = new_data.get('Price', existing_record.avg_price)  # فعلاً از همان Price استفاده می‌کنیم
        existing_record.lowest_price = new_data.get('MinPrice', existing_record.lowest_price)
        existing_record.highest_price = new_data.get('MaxPrice', existing_record.highest_price)
        existing_record.volume = int(new_data.get('Quantity', existing_record.volume or 0)) if new_data.get('Quantity') else existing_record.volume
        existing_record.value = new_data.get('TotalPrice', existing_record.value)
        existing_record.unit = new_data.get('Unit', existing_record.unit)[:20]
        existing_record.source = 'scroll_time'
        existing_record.save()
    
    def _create_alldata_record(self, record: Dict[str, Any], scroll_request: ScrollTimeRequest) -> DataManagementAllData:
        """ایجاد رکورد جدید در مدل data_management.AllData براساس ساختار Iran Exchange API"""
        
        shamsi_date_str = record.get('date', '')  # 1403/05/01
        
        return DataManagementAllData.objects.create(
            # اطلاعات اصلی کالا
            commodity_name=record.get('GoodsName', 'نامشخص')[:100],
            symbol=record.get('Symbol', '')[:50],
            hall=record.get('Hall', '')[:100],
            producer=record.get('Producer', '')[:200],
            contract_type=record.get('ContractType', '')[:50],
            
            # قیمت‌ها
            final_price=record.get('Price', 0),
            transaction_value=record.get('TotalPrice', 0),
            lowest_price=record.get('MinPrice', 0),
            highest_price=record.get('MaxPrice', 0),
            base_price=record.get('BasePrice', 0),
            
            # حجم‌ها
            offer_volume=int(record.get('OfferVolume', 0)) if record.get('OfferVolume') else 0,
            demand_volume=int(record.get('DemandVolume', 0)) if record.get('DemandVolume') else 0,
            contract_volume=int(record.get('Quantity', 0)) if record.get('Quantity') else 0,
            unit=record.get('Unit', '')[:20],
            
            # تاریخ
            transaction_date=shamsi_date_str,
            
            # اطلاعات اضافی
            supplier=record.get('Supplier', '')[:200],
            broker=record.get('Broker', '')[:100],
            settlement_type=record.get('SettlementType', '')[:50],
            delivery_date=record.get('DeliveryDate', ''),
            warehouse=record.get('Warehouse', ''),
            settlement_date=record.get('SettlementDate', ''),
            
            # شناسه‌ها
            x_talar_report_pk=record.get('XTalarReportPK'),
            arzeh_pk=record.get('ArzehPK'),
            packet_name=record.get('PacketName', ''),
            currency=record.get('Currency', ''),
            
            # داده خام
            raw_data=record,
            
            # متادیتا
            source=f'scroll_time_{scroll_request.id}',
            api_endpoint='https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList'
        )
    
    def _update_alldata_record(self, existing_record: DataManagementAllData, new_data: Dict[str, Any], scroll_request: ScrollTimeRequest) -> None:
        """بروزرسانی رکورد موجود در مدل data_management.AllData براساس ساختار Iran Exchange API"""
        existing_record.commodity_name = new_data.get('GoodsName', existing_record.commodity_name)[:100]
        existing_record.symbol = new_data.get('Symbol', existing_record.symbol)[:50]
        existing_record.hall = new_data.get('Hall', existing_record.hall)[:100]
        existing_record.producer = new_data.get('Producer', existing_record.producer)[:200]
        existing_record.contract_type = new_data.get('ContractType', existing_record.contract_type)[:50]
        
        # قیمت‌ها
        existing_record.final_price = new_data.get('Price', existing_record.final_price)
        existing_record.transaction_value = new_data.get('TotalPrice', existing_record.transaction_value)
        existing_record.lowest_price = new_data.get('MinPrice', existing_record.lowest_price)
        existing_record.highest_price = new_data.get('MaxPrice', existing_record.highest_price)
        existing_record.base_price = new_data.get('BasePrice', existing_record.base_price)
        
        # حجم‌ها
        existing_record.offer_volume = int(new_data.get('OfferVolume', existing_record.offer_volume or 0)) if new_data.get('OfferVolume') else existing_record.offer_volume
        existing_record.demand_volume = int(new_data.get('DemandVolume', existing_record.demand_volume or 0)) if new_data.get('DemandVolume') else existing_record.demand_volume
        existing_record.contract_volume = int(new_data.get('Quantity', existing_record.contract_volume or 0)) if new_data.get('Quantity') else existing_record.contract_volume
        existing_record.unit = new_data.get('Unit', existing_record.unit)[:20]
        
        # اطلاعات اضافی
        existing_record.supplier = new_data.get('Supplier', existing_record.supplier)[:200]
        existing_record.broker = new_data.get('Broker', existing_record.broker)[:100]
        existing_record.settlement_type = new_data.get('SettlementType', existing_record.settlement_type)[:50]
        existing_record.delivery_date = new_data.get('DeliveryDate', existing_record.delivery_date)
        existing_record.warehouse = new_data.get('Warehouse', existing_record.warehouse)
        existing_record.settlement_date = new_data.get('SettlementDate', existing_record.settlement_date)
        
        # شناسه‌ها
        existing_record.x_talar_report_pk = new_data.get('XTalarReportPK', existing_record.x_talar_report_pk)
        existing_record.arzeh_pk = new_data.get('ArzehPK', existing_record.arzeh_pk)
        existing_record.packet_name = new_data.get('PacketName', existing_record.packet_name)
        existing_record.currency = new_data.get('Currency', existing_record.currency)
        
        # داده خام و متادیتا
        existing_record.raw_data = new_data
        existing_record.source = f'scroll_time_{scroll_request.id}'
        
        existing_record.save()
    
    def _create_import_log(self, scroll_request: ScrollTimeRequest, stats: Dict[str, int]):
        """ایجاد لاگ وارد کردن داده"""
        DataImportLog.objects.create(
            commodity_name=f"{scroll_request.main_category.name} -> {scroll_request.category.name} -> {scroll_request.subcategory.name}",
            start_date=convert_shamsi_to_gregorian(scroll_request.start_date_shamsi),
            end_date=convert_shamsi_to_gregorian(scroll_request.end_date_shamsi),
            total_records=stats['total_records'],
            imported_records=stats['imported_records'],
            updated_records=stats['updated_records'],
            duplicate_records=stats['duplicate_records'],
            error_records=stats['error_records'],
            status='success' if stats['error_records'] == 0 else 'partial',
            created_by=scroll_request.created_by
        )


class DataPreviewService:
    """سرویس پیش‌نمایش داده‌ها قبل از ذخیره"""
    
    @staticmethod
    def get_preview_data(scroll_request: ScrollTimeRequest, limit: int = 5) -> Dict[str, Any]:
        """
        دریافت نمونه داده‌ها برای پیش‌نمایش
        
        Args:
            scroll_request: درخواست Scroll Time
            limit: تعداد رکوردهای نمونه
            
        Returns:
            Dict شامل نمونه داده‌ها و آمار
        """
        if not scroll_request.response_data:
            return {
                'success': False,
                'error': 'هیچ داده‌ای برای پیش‌نمایش وجود ندارد'
            }
        
        data_list = scroll_request.response_data
        if not isinstance(data_list, list):
            data_list = [data_list]
        
        # نمونه رکوردها
        sample_records = data_list[:limit]
        
        # آمار کلی
        stats = {
            'total_records': len(data_list),
            'sample_count': len(sample_records),
            'categories': scroll_request.main_category.name,
            'subcategories': f"{scroll_request.category.name} -> {scroll_request.subcategory.name}",
            'date_range': f"{scroll_request.start_date_shamsi} تا {scroll_request.end_date_shamsi}"
        }
        
        return {
            'success': True,
            'stats': stats,
            'sample_records': sample_records,
            'scroll_request_id': scroll_request.id
        }
