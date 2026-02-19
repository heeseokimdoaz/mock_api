const PAGE_SIZE = 10;
let currentPage = 0;
let trendChart = null;

const SITE_TYPE_LABELS = {
    media: "매스미디어",
    comm: "커뮤니티",
    twitter: "X(트위터)",
    youtube: "유튜브",
};

const SITE_TYPE_COLORS = {
    media: "#2563eb",
    comm: "#d97706",
    twitter: "#6366f1",
    youtube: "#e11d48",
};

const POLARITY_LABELS = { "0": "중립", "1": "긍정", "2": "부정" };

function dateToParam(dateStr) {
    return dateStr.replace(/-/g, "") + "000000";
}

function dateToParamEnd(dateStr) {
    return dateStr.replace(/-/g, "") + "235959";
}

function formatDate(raw) {
    if (raw.length < 8) return raw;
    const y = raw.slice(0, 4);
    const m = raw.slice(4, 6);
    const d = raw.slice(6, 8);
    if (raw.length >= 14) {
        const hh = raw.slice(8, 10);
        const mm = raw.slice(10, 12);
        return `${y}-${m}-${d} ${hh}:${mm}`;
    }
    return `${y}-${m}-${d}`;
}

function getFilters() {
    const from = document.getElementById("fromDate").value;
    const to = document.getElementById("toDate").value;
    const siteType = document.getElementById("siteType").value;
    return {
        from_date: dateToParam(from),
        to_date: dateToParamEnd(to),
        site_type: siteType || null,
    };
}

async function fetchTrend(filters) {
    const params = new URLSearchParams({
        from_date: filters.from_date,
        to_date: filters.to_date,
    });
    if (filters.site_type) params.set("site_type", filters.site_type);
    const resp = await fetch(`/api/trend?${params}`);
    return resp.json();
}

async function fetchDocs(filters, offset) {
    const params = new URLSearchParams({
        from_date: filters.from_date,
        to_date: filters.to_date,
        offset: offset.toString(),
        size: PAGE_SIZE.toString(),
    });
    if (filters.site_type) params.set("site_type", filters.site_type);
    const resp = await fetch(`/api/documents?${params}`);
    return resp.json();
}

function renderTrendChart(data) {
    const ctx = document.getElementById("trendChart").getContext("2d");

    const dates = [...new Set(data.map((d) => d.create_date))].sort();
    const siteTypes = [...new Set(data.map((d) => d.site_type))];

    const datasets = siteTypes.map((st) => {
        const countMap = {};
        data.filter((d) => d.site_type === st).forEach((d) => {
            countMap[d.create_date] = d.doc_count;
        });
        return {
            label: SITE_TYPE_LABELS[st] || st,
            data: dates.map((d) => countMap[d] || 0),
            borderColor: SITE_TYPE_COLORS[st] || "#999",
            backgroundColor: (SITE_TYPE_COLORS[st] || "#999") + "33",
            fill: true,
            tension: 0.3,
        };
    });

    if (trendChart) trendChart.destroy();

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: dates.map((d) => formatDate(d)),
            datasets,
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "top" },
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: "문서 수" } },
            },
        },
    });
}

function renderDocTable(data) {
    const tbody = document.getElementById("docBody");
    tbody.innerHTML = "";

    data.forEach((doc) => {
        const tr = document.createElement("tr");

        const polarityClass =
            doc.polarity === "1"
                ? "polarity-positive"
                : doc.polarity === "2"
                ? "polarity-negative"
                : "polarity-neutral";

        const siteClass = `site-${doc.site_type}`;
        const titleOrContent = doc.title || doc.content.slice(0, 80) + "...";

        tr.innerHTML = `
            <td>${formatDate(doc.create_date)}</td>
            <td><span class="site-badge ${siteClass}">${SITE_TYPE_LABELS[doc.site_type] || doc.site_type}</span></td>
            <td>${doc.site_name}</td>
            <td class="content-cell" title="${doc.content.slice(0, 200).replace(/"/g, '&quot;')}">${titleOrContent}</td>
            <td class="${polarityClass}">${POLARITY_LABELS[doc.polarity] || "중립"}</td>
            <td>${doc.url ? `<a href="${doc.url}" target="_blank">원문</a>` : "-"}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function loadData() {
    currentPage = 0;
    const filters = getFilters();

    const [trendResp, docResp] = await Promise.all([
        fetchTrend(filters),
        fetchDocs(filters, 0),
    ]);

    if (trendResp.status === "success") {
        renderTrendChart(trendResp.data);
    }
    if (docResp.status === "success") {
        renderDocTable(docResp.data);
        const total = trendResp.data.reduce((sum, d) => sum + d.doc_count, 0);
        document.getElementById("docCount").textContent = `(총 ${total}건)`;
    }
    updatePageInfo();
}

async function loadPage() {
    const filters = getFilters();
    const docResp = await fetchDocs(filters, currentPage * PAGE_SIZE);
    if (docResp.status === "success") {
        renderDocTable(docResp.data);
    }
    updatePageInfo();
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        loadPage();
    }
}

function nextPage() {
    currentPage++;
    loadPage();
}

function updatePageInfo() {
    document.getElementById("pageInfo").textContent = `${currentPage + 1} 페이지`;
}

// 페이지 로드 시 자동 조회
window.addEventListener("DOMContentLoaded", loadData);
