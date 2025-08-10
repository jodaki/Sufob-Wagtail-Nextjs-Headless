import { getApiUrl } from "./api";

export const indexPages = async () => {
    const apiUrl = getApiUrl();
    return await fetch(
        `${apiUrl}/api/v2/pages/?${new URLSearchParams({
            type: "blog.BlogPageIndex",
            slug: "blog-index",
            fields: "intro",
        })}`,
        {
            cache: "no-store",
            headers: {
                Accept: "application/json",
            },
        }
    ).then((response) => response.json());
};
export const fetchPosts = async (
    limit,
    offset,
    categories = null,
    tags = null
) => {
    const apiUrl = getApiUrl();
    const index = await indexPages();
    
    // Check if we have a valid index page
    if (!index || !index.items || index.items.length === 0) {
        return { items: [], meta: { total_count: 0 } };
    }
    
    const indexPage = index.items[0];
    const params = {
        type: "blog.BlogPage",
        child_of: indexPage.id,
        fields: [
            "id",
            "title",
            "tags",
            "categories(name,slug)",
            "header_image",
            "content",
            "md_content",
            "view_count",
            "seo_title",
            "search_description",
            "md_headings",
            "last_published_at",
        ].join(","),
        order: "-first_published_at",
    };
    if (limit) params.limit = limit;
    if (offset) params.offset = offset;
    if (categories) params.categories = categories;
    if (tags) params.tags = tags;
    const data = await fetch(
        `${apiUrl}/api/v2/pages/?${new URLSearchParams(params)}`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    return data;
};

export const getPostBySlug = async (slug) => {
    const apiUrl = getApiUrl();
    const posts = await fetch(
        `${apiUrl}/api/v2/pages/?${new URLSearchParams({
            type: "blog.BlogPage",
            slug: slug,
            fields: [
                "id",
                "title",
                "tags",
                "categories(name,slug)",
                "header_image",
                "content",
                "md_content",
                "view_count",
                "headings",
                "seo_title",
                "search_description",
                "md_headings",
                "last_published_at",
            ].join(","),
        })}`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    
    // Check if we have a result
    if (!posts || !posts.items || posts.items.length === 0) {
        return null;
    }
    
    return posts.items[0];
};

export const getDraftByToken = async (content_type, token) => {
    const apiUrl = getApiUrl();
    const post = await fetch(
        `${apiUrl}/api/v2/page_preview/?content_type=${content_type}&token=${token}&format=json`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    return post;
};

export const getCategories = async () => {
    // Mock data to avoid backend dependency
    const mockCategories = [
        {
            id: 1,
            title: "بلاگ",
            slug: "blog",
            description: "مقالات و اخبار"
        },
        {
            id: 2,
            title: "قیمت‌ها",
            slug: "prices",
            description: "قیمت کالاها"
        },
        {
            id: 3,
            title: "تحلیل",
            slug: "analysis",
            description: "تحلیل بازار"
        }
    ];
    
    // Return mock data instead of fetching from backend
    return mockCategories;
};
export const getCategory = async (slug) => {
    const categories = await getCategories();
    const category = categories.filter((c) => c.slug === slug);
    return category[0];
};

export const getPosts = async (limit, offset) => {
    const posts = await fetchPosts(limit, offset);
    // let filteredPosts = posts.items.filter((post) => !post.draft);
    return posts;
};

export const getTags = async (limit) => {
    const posts = await fetchPosts(limit);
    const tags = new Set();

    posts.items.forEach((post) => {
        post.tags.forEach((tag) => {
            // 将tag对象转换为字符串
            const tagString = JSON.stringify(tag);
            tags.add(tagString);
        });
    });

    // 将字符串转换回对象并返回
    return Array.from(tags).map((tagString) => JSON.parse(tagString));
};

export const getTag = async (slug) => {
    const apiUrl = getApiUrl();
    const tag = await fetch(
        `${apiUrl}/api/v2/tags/?${new URLSearchParams({
            slug: slug,
            fields: ["id", "name", "slug"].join(","),
        })}`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    return tag.items[0];
};
export const getPostByTag = async (limit, offset, slug) => {
    const posts = await fetchPosts(limit, offset, null, slug);
    return posts;
};

export const filterPostsByCategory = async (limit, offset, categorySlug) => {
    const category = await getCategory(categorySlug);
    const filteredPosts = await fetchPosts(limit, offset, category.id);
    return filteredPosts;
};

export const searchPosts = async (query) => {
    const apiUrl = getApiUrl();
    return await fetch(
        `${apiUrl}/v2/pages/?${new URLSearchParams({
            search: query,
            fields: [
                "id",
                "title",
                // "tags",
                // "categories(name,slug)",
                // "header_image",
                // "content",
                // "md_content",
            ].join(","),
        })}`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
};

// ==========================================
// Price/Transaction related functions (Wagtail API)
// ==========================================

export const getPriceIndexPages = async () => {
    const apiUrl = getApiUrl();
    return await fetch(
        `${apiUrl}/api/v2/pages/?${new URLSearchParams({
            type: "price_display.PriceIndexPage",
            fields: "intro",
        })}`,
        {
            cache: "no-store",
            headers: {
                Accept: "application/json",
            },
        }
    ).then((response) => response.json());
};

export const getPricePages = async () => {
    const apiUrl = getApiUrl();
    return await fetch(
        `${apiUrl}/api/v2/pages/?${new URLSearchParams({
            type: "price_display.PricePage",
            fields: [
                "id",
                "title",
                "slug",
                "get_main_category_name",
                "get_category_name",
                "get_subcategory_name",
                "chart_description",
                "chart_days",
            ].join(","),
        })}`,
        {
            cache: "no-store",
            headers: {
                Accept: "application/json",
            },
        }
    ).then((response) => response.json());
};

export const getPricePageBySlug = async (slug) => {
    const apiUrl = getApiUrl();
    const pages = await fetch(
        `${apiUrl}/api/v2/pages/?${new URLSearchParams({
            type: "price_display.PricePage",
            slug: slug,
            fields: [
                "id",
                "title",
                "get_main_category_name",
                "get_category_name", 
                "get_subcategory_name",
                "chart_description",
                "chart_days",
                "get_latest_posts",
            ].join(","),
        })}`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    
    if (!pages || !pages.items || pages.items.length === 0) {
        return null;
    }
    
    return pages.items[0];
};

export const getTransactionsFromWagtail = async (commodity = null, fromDate = null, toDate = null) => {
    const apiUrl = getApiUrl();
    const params = {};
    if (commodity) params.commodity = commodity;
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;
    
    const data = await fetch(
        `${apiUrl}/api/v2/transactions/?${new URLSearchParams(params)}`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    return data;
};

export const getCommoditiesFromWagtail = async () => {
    const apiUrl = getApiUrl();
    const data = await fetch(
        `${apiUrl}/api/v2/commodities/`,
        {
            cache: "no-store",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then((res) => res.json());
    return data.items || [];
};

export const getPriceChartData = async (commodity, days = 30) => {
    const transactions = await getTransactionsFromWagtail(commodity);
    
    if (!transactions.items || transactions.items.length === 0) {
        return [];
    }
    
    // Filter and prepare chart data
    const chartData = transactions.items
        .slice(0, days)
        .map(item => ({
            time: item.transaction_date,
            value: parseFloat(item.final_price) || parseFloat(item.base_price) || 0,
            volume: item.contract_volume || 0,
        }))
        .sort((a, b) => a.time.localeCompare(b.time));
    
    return chartData;
};

// New TradingView-friendly series API
export const getPriceSeries = async (page, period = 'daily', days = null) => {
    // Mock price data to avoid backend dependency
    const mockData = {
        '1D': [
            { time: '2024-08-09', value: 150000 },
            { time: '2024-08-08', value: 148000 },
            { time: '2024-08-07', value: 152000 },
            { time: '2024-08-06', value: 149000 },
            { time: '2024-08-05', value: 151000 }
        ],
        '1W': [
            { time: '2024-08-09', value: 150000 },
            { time: '2024-08-02', value: 145000 },
            { time: '2024-07-26', value: 140000 },
            { time: '2024-07-19', value: 142000 },
            { time: '2024-07-12', value: 138000 }
        ],
        '1M': [
            { time: '2024-08-01', value: 150000 },
            { time: '2024-07-01', value: 140000 },
            { time: '2024-06-01', value: 135000 },
            { time: '2024-05-01', value: 145000 },
            { time: '2024-04-01', value: 132000 }
        ],
        '1Y': [
            { time: '2024-01-01', value: 120000 },
            { time: '2023-01-01', value: 110000 },
            { time: '2022-01-01', value: 105000 },
            { time: '2021-01-01', value: 95000 },
            { time: '2020-01-01', value: 90000 }
        ]
    };
    
    // Map period parameter to mock data
    const periodMap = {
        'daily': '1D',
        'weekly': '1W', 
        'monthly': '1M',
        'yearly': '1Y'
    };
    
    const dataKey = periodMap[period] || '1D';
    return mockData[dataKey] || mockData['1D'];
};
