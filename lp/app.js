const fallback = {
  product_name: "充電式コードレス卓上クリーナー",
  lp_hook: "1日10分の掃除を3分に。散らかりを一気に吸引",
  price_jpy: 5980,
  benefits: ["片手サイズで置き場所に困らない", "USB充電でコードレス運用", "食べこぼしや作業後の粉末を素早く回収"],
  values: [
    { title: "時短", body: "毎日の細かい掃除を短時間に圧縮" },
    { title: "手軽さ", body: "気づいた瞬間にすぐ使える" },
    { title: "安心", body: "30日返品保証で試しやすい" }
  ],
  comparison: [
    ["起動までの手間", "ワンタッチ", "電源準備が必要"],
    ["収納性", "コンパクト", "かさばりやすい"],
    ["日々の使いやすさ", "高い", "普通"]
  ],
  reviews: [
    { name: "34歳・共働き", text: "食後テーブル掃除が本当に早くなった" },
    { name: "29歳・一人暮らし", text: "デスクの消しカス掃除にちょうどいい" },
    { name: "41歳・2児ママ", text: "子どもの食べこぼし対策で毎日使ってる" }
  ],
  faq: [
    { q: "配送日数は？", a: "通常5〜10日以内に発送します。" },
    { q: "返品できますか？", a: "到着後30日以内なら返品可能です。" },
    { q: "支払い方法は？", a: "クレジットカード、各種ウォレットに対応予定です。" }
  ]
};

function yen(price) {
  return `¥${Number(price).toLocaleString("ja-JP")}`;
}

function paint(data) {
  document.getElementById("product-name").textContent = data.product_name;
  document.getElementById("hero-hook").textContent = data.lp_hook;
  document.getElementById("price").textContent = yen(data.price_jpy);
  document.getElementById("old-price").textContent = yen(Math.round(data.price_jpy * 1.25));
  document.getElementById("sticky-copy").textContent = `${data.product_name}を本日価格で`; 

  document.getElementById("benefits").innerHTML = data.benefits.map((item) => `<li>${item}</li>`).join("");

  document.getElementById("value-cards").innerHTML = data.values
    .map((v) => `<article class="info-box"><h3>${v.title}</h3><p>${v.body}</p></article>`)
    .join("");

  document.getElementById("comparison-body").innerHTML = data.comparison
    .map((row) => `<tr><td>${row[0]}</td><td>${row[1]}</td><td>${row[2]}</td></tr>`)
    .join("");

  document.getElementById("reviews").innerHTML = data.reviews
    .map((r) => `<article class="info-box"><h3>${r.name}</h3><p>\"${r.text}\"</p></article>`)
    .join("");

  document.getElementById("faq").innerHTML = data.faq
    .map((f) => `<article class="faq-item"><h3>Q. ${f.q}</h3><p>A. ${f.a}</p></article>`)
    .join("");
}

fetch("lp_data.json")
  .then((res) => (res.ok ? res.json() : fallback))
  .then((data) => paint(data))
  .catch(() => paint(fallback));
