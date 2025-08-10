
"use client";
import * as React from "react";
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';

const PriceSummary = ({ priceData = null, transactionData = null }) => {
  // Default price data
  const defaultPriceData = {
    finalPriceAvg: "54,540",
    finalPrice: "54,540",
    lowestPrice: "54,540",
    highestPrice: "54,540",
    weeklyRange: "50,000-50,300",
    monthlyRange: "۹۱.۲۸-۱۱۲.۳۹",
    monthlyChange: "-۱۰.۳۵ %",
  };
  // Default transaction data
  const defaultTransactionData = {
    settlementType: "نقدی",
    transactionDate: "1404/04/30",
    contractVolume: "45,000",
    demand: "45,000",
    supplyVolume: "50,000",
    basePrice: "54,540",
    transactionValue: "654,480,000",
  };
  // اگر داده به صورت آرایه ارسال شد، فقط اولین آیتم را نمایش بده
  const price = Array.isArray(priceData) ? (priceData[0] || defaultPriceData) : (priceData || defaultPriceData);
  const transaction = Array.isArray(transactionData) ? (transactionData[0] || defaultTransactionData) : (transactionData || defaultTransactionData);

  return (
    <Box sx={{ overflow: 'auto', maxHeight: 400, p: 2 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%' }}>
            <CardHeader title={<span style={{ fontWeight: 600, fontSize: '1.1rem' }}>اطلاعات قیمت</span>} sx={{ bgcolor: '#f5f5f5', py: 1 }} />
            <CardContent sx={{ p: 0 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>قیمت پایانی میانگین موزون</TableCell>
                    <TableCell align="left" sx={{ fontWeight: 'bold' }}>{price.finalPriceAvg}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>قیمت پایانی</TableCell>
                    <TableCell align="left" sx={{ fontWeight: 'bold' }}>{price.finalPrice}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>پایین‌ترین</TableCell>
                    <TableCell align="left">{price.lowestPrice}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>بالاترین</TableCell>
                    <TableCell align="left">{price.highestPrice}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>محدوده هفتگی</TableCell>
                    <TableCell align="left">{price.weeklyRange}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>محدوده ۳۰ روزه</TableCell>
                    <TableCell align="left">{price.monthlyRange}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>تغییر ماهه</TableCell>
                    <TableCell align="left" sx={{ color: 'error.main', fontWeight: 'bold' }}>{price.monthlyChange}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%' }}>
            <CardHeader title={<span style={{ fontWeight: 600, fontSize: '1.1rem' }}>اطلاعات معامله</span>} sx={{ bgcolor: '#f5f5f5', py: 1 }} />
            <CardContent sx={{ p: 0 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>نوع تسویه</TableCell>
                    <TableCell align="left">{transaction.settlementType}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>تاریخ معامله</TableCell>
                    <TableCell align="left">{transaction.transactionDate}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>حجم قراردادها</TableCell>
                    <TableCell align="left">{transaction.contractVolume}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>تقاضا</TableCell>
                    <TableCell align="left">{transaction.demand}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>حجم عرضه</TableCell>
                    <TableCell align="left">{transaction.supplyVolume}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>قیمت پایه عرضه</TableCell>
                    <TableCell align="left" sx={{ fontWeight: 'bold' }}>{transaction.basePrice}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>ارزش معامله (هزارریال)</TableCell>
                    <TableCell align="left" sx={{ fontWeight: 'bold' }}>{transaction.transactionValue}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PriceSummary;
