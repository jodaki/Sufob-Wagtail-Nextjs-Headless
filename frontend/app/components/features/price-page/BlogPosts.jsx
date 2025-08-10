"use client";

import React from 'react';

const BlogPosts = ({ posts = null, showCount = 3 }) => {
  
  // Default blog posts data
  const defaultPosts = [
    {
      id: 1,
      title: 'تحلیل بازار کالا در هفته گذشته',
      excerpt: 'بررسی روند قیمت‌ها و معاملات بازار کالا در هفته گذشته نشان می‌دهد که قیمت‌ها روند صعودی داشته و حجم معاملات نیز افزایش یافته است.',
      date: '۱۴۰۴/۰۴/۳۰',
      category: 'تحلیل بازار',
      readTime: '۵ دقیقه',
      image: '/images/blog/market-analysis.jpg',
      slug: 'market-analysis-last-week'
    },
    {
      id: 2,
      title: 'پیش‌بینی قیمت کالاهای اساسی',
      excerpt: 'با توجه به شرایط اقتصادی و سیاست‌های جدید، پیش‌بینی می‌شود که قیمت کالاهای اساسی در ماه‌های آینده تغییرات قابل توجهی خواهد داشت.',
      date: '۱۴۰۴/۰۴/۲۸',
      category: 'پیش‌بینی',
      readTime: '۷ دقیقه',
      image: '/images/blog/price-prediction.jpg',
      slug: 'commodity-price-prediction'
    },
    {
      id: 3,
      title: 'راهنمای سرمایه‌گذاری در بازار کالا',
      excerpt: 'برای سرمایه‌گذاری موفق در بازار کالا، باید نکات مهمی را در نظر گرفت که در ادامه به بررسی استراتژی‌های مختلف خواهیم پرداخت.',
      date: '۱۴۰۴/۰۴/۲۶',
      category: 'راهنما',
      readTime: '۱۰ دقیقه',
      image: '/images/blog/investment-guide.jpg',
      slug: 'commodity-investment-guide'
    },
    {
      id: 4,
      title: 'تاثیر تحولات جهانی بر قیمت کالاها',
      excerpt: 'تحولات سیاسی و اقتصادی جهان همواره تاثیر مستقیمی بر قیمت کالاها داشته است. در این مقاله به بررسی این تاثیرات می‌پردازیم.',
      date: '۱۴۰۴/۰۴/۲۴',
      category: 'تحلیل',
      readTime: '۶ دقیقه',
      image: '/images/blog/global-impact.jpg',
      slug: 'global-events-commodity-prices'
    }
  ];

  const blogPosts = posts || defaultPosts;
  const displayPosts = blogPosts.slice(0, showCount);

  return (
    <div className="blog-posts-container">
      <div className="card">
        <div className="card-header">
          <h6 className="mb-0">مقالات مرتبط</h6>
        </div>
        <div className="card-body">
          <div className="row">
            {displayPosts.map((post) => (
              <div key={post.id} className="col-md-6 col-lg-4 mb-4">
                <div className="card h-100 shadow-sm border-0">
                  <div 
                    className="card-img-top d-flex align-items-center justify-content-center"
                    style={{ 
                      height: '180px', 
                      backgroundColor: '#f8f9fa',
                      backgroundImage: 'linear-gradient(45deg, #e9ecef 25%, transparent 25%), linear-gradient(-45deg, #e9ecef 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e9ecef 75%), linear-gradient(-45deg, transparent 75%, #e9ecef 75%)',
                      backgroundSize: '20px 20px',
                      backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
                    }}
                  >
                    <div className="text-center">
                      <i className="fas fa-image fa-2x text-muted mb-2"></i>
                      <div className="small text-muted">تصویر مقاله</div>
                    </div>
                  </div>
                  <div className="card-body d-flex flex-column">
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <span className="badge bg-primary rounded-pill">{post.category}</span>
                      <small className="text-muted">
                        <i className="far fa-clock me-1"></i>
                        {post.readTime}
                      </small>
                    </div>
                    
                    <h6 className="card-title">{post.title}</h6>
                    <p className="card-text text-muted flex-grow-1 small">{post.excerpt}</p>
                    
                    <div className="d-flex justify-content-between align-items-center mt-auto pt-2 border-top">
                      <small className="text-muted">
                        <i className="far fa-calendar me-1"></i>
                        {post.date}
                      </small>
                      <a href={`/blog/${post.slug}`} className="btn btn-outline-primary btn-sm">
                        ادامه مطلب
                        <i className="fas fa-arrow-left ms-1"></i>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {blogPosts.length > showCount && (
            <div className="text-center mt-3 pt-3 border-top">
              <a href="/blog" className="btn btn-primary">
                <i className="fas fa-newspaper me-2"></i>
                مشاهده همه مقالات
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BlogPosts;
