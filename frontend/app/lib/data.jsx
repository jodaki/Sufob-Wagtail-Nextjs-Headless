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
    const apiUrl = getApiUrl();
    const categories = await fetch(`${apiUrl}/api/v2/categories/`, {
        cache: "no-store",
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    }).then((res) => res.json());
    return categories.items;
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
            type: "prices.PriceIndexPage",
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
            type: "prices.PricePage",
            fields: [
                "id",
                "title",
                "slug",
                "commodity_name",
                "chart_description",
                "show_statistics",
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
            type: "prices.PricePage",
            slug: slug,
            fields: [
                "id",
                "title",
                "commodity_name",
                "chart_description",
                "show_statistics",
                "chart_days",
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
