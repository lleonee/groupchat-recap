// Sample chat generator for the "Örnek sunum oluştur" button.
// Builds a fictional but realistic WhatsApp group export (iOS format) entirely in the browser:
// six friends, ~20 months of messages, each person with their own habits (night owl, morning person,
// emoji lover, quiet one who goes on Erasmus...). A fixed seed keeps the sample identical on every click.

const SAMPLE_GROUP_NAME = "Kanka Ekibi";
const SAMPLE_START = new Date(2025, 1, 10);   // 10.02.2025
const SAMPLE_END = new Date(2026, 9, 17);     // 17.10.2026

// Seeded PRNG (mulberry32) so the sample is deterministic
function sampleRng(seed) {
    let a = seed >>> 0;
    return function () {
        a = (a + 0x6D2B79F5) >>> 0;
        let t = a;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

const SAMPLE_MEMBERS = [
    {
        name: "Mert Demir", first: "Mert", weight: 1.7, night: 2.8, morning: 0.25, starter: 1.0,
        lower: true, punct: 0.05, emoji: 0.07, caps: 0.04, swear: 0.06, media: 0.05, link: 0.02, burst: 0.45,
        emojis: ["💀", "😂", "🔥", "🤣"], laughs: ["SKSKSKSKSK", "sjsjsjsj", "AHSJDJSJ", "skssksks 💀"],
        swears: ["amk", "aq", "mal mısın", "salak"]
    },
    {
        name: "Zeynep Arslan", first: "Zeynep", weight: 1.25, night: 0.2, morning: 2.8, starter: 2.2,
        lower: false, punct: 0.8, emoji: 0.18, caps: 0.0, swear: 0.004, media: 0.04, link: 0.03, burst: 0.25, long: 0.4,
        emojis: ["😊", "🙏", "❤️", "✨"], laughs: ["Hahahah", "Ahahaha çok iyi", "Hahaha ölüyorum"],
        swears: ["salak"]
    },
    {
        name: "Elif Kaya", first: "Elif", weight: 1.35, night: 1.0, morning: 0.9, starter: 1.1,
        lower: true, punct: 0.2, emoji: 0.6, caps: 0.02, swear: 0.01, media: 0.07, link: 0.03, burst: 0.4,
        emojis: ["😂", "😭", "❤️", "🥹", "💅", "🙈", "😍"], laughs: ["AHAHAHAHAHAH 😂😂", "ahahahah 😭", "öldüm 😂😂😂", "AHAHSHAHA"],
        swears: ["aptal"]
    },
    {
        name: "Ahmet Yılmaz", first: "Ahmet", weight: 1.0, night: 0.8, morning: 1.4, starter: 0.8,
        lower: false, punct: 0.4, emoji: 0.12, caps: 0.01, swear: 0.02, media: 0.03, link: 0.04, burst: 0.2,
        emojis: ["👍", "😄", "👌"], laughs: ["hahaha", "haha iyiymiş", "hahahah"],
        swears: ["manyak", "salak"]
    },
    {
        name: "Burak Şahin", first: "Burak", weight: 0.95, night: 1.6, morning: 0.5, starter: 0.9,
        lower: true, punct: 0.05, emoji: 0.1, caps: 0.04, swear: 0.04, media: 0.2, link: 0.1, burst: 0.5,
        emojis: ["🗿", "😂", "🤡"], laughs: ["ahdjsjsjsj", "SJSJSJSJ", "hsjdjsj 🗿"],
        swears: ["aq", "manyak", "mal"]
    },
    {
        name: "Deniz Çelik", first: "Deniz", weight: 0.45, night: 0.7, morning: 1.0, starter: 0.5,
        lower: true, punct: 0.3, emoji: 0.2, caps: 0.0, swear: 0.0, media: 0.06, link: 0.02, burst: 0.15,
        emojis: ["🙂", "🥲", "🌍"], laughs: ["ksksks", "hahah", "jfjsjsj"],
        swears: [],
        // Erasmus: no messages at all for almost three months
        away: [[new Date(2025, 8, 6), new Date(2025, 10, 27)]]
    }
];

// Topics: an opener starts the session, replies keep it going. {n} = another member's first name.
const SAMPLE_TOPICS = {
    plan: {
        w: 3,
        open: [
            "akşam ne yapıyoruz", "bu cumartesi boş olan var mı", "hafta sonu bir şeyler yapalım artık",
            "bu akşam çıkıyor muyuz", "kadıköyde buluşalım mı bugün", "yarın kahvaltıya gidelim mi",
            "cuma akşamı bizde film gecesi var gelen?", "beyoğlunda yeni bir bar açılmış gidelim mi",
            "uzun zamandır toplanmadık bu hafta bir araya gelelim", "pazar günü moda sahile inelim mi"
        ],
        reply: [
            "ben varım", "bende varım", "saat kaçta", "ben 8 gibi çıkarım", "nerede buluşuyoruz",
            "ben biraz geç kalırım", "tamam olur", "ben bu akşam yokum ya", "yarın sınavım var gelemem",
            "kim geliyor yazın", "ben kesin geliyorum", "yer ayırtalım mı", "her zamanki yer mi",
            "metrodan inince yazarım", "8.30 iskele önü", "{n} sen geliyor musun", "{n} yine gelmeyecek biliyorum",
            "evet geliyorum", "belki uğrarım", "araba bende alırım sizi", "hesabı bölüşürüz", "tamam o zaman 9da orada",
            "ben yoldayım", "5 dakikaya oradayım", "siz başlayın ben geliyorum", "geldim neredesiniz",
            "masa ayırttım 4 kişilik", "6 kişi olursak sığmayız", "o zaman başka yere bakalım"
        ]
    },
    school: {
        w: 2.2,
        open: [
            "yarınki sınav kaçta", "ödevi bitiren var mı", "hocanın attığı maili gördünüz mü",
            "final haftası başlıyor kafayı yiyeceğim", "notlar açıklanmış", "kütüphanede yer var mı şu an",
            "proje teslimi ne zamandı", "derse giren var mı bugün", "staj başvuruları açılmış",
            "slaytları atabilir misiniz"
        ],
        reply: [
            "hiç çalışmadım", "ben de bitiremedim", "cuma 23.59", "pazartesi saat 10da", "kütüphanedeyim gelin",
            "hoca çok zor sormuş", "geçerim herhalde", "yandık", "ben 70 aldım", "bütünlemeye kaldım galiba",
            "notları atarım akşam", "{n} sende ders notları vardı", "ders iptal olmuş", "yoklama alıyor mu",
            "imza atar mısın benim yerime", "ders çok sıkıcıydı", "proje grubunda kimler var", "ben başvurdum",
            "mülakata çağırdılar", "cv mi baktınız", "tebrikler", "sınavdan çıktım boş yaptım",
            "bütün gece çalıştım", "kahve şart", "sonra kantinde buluşalım"
        ]
    },
    gossip: {
        w: 1.6,
        open: [
            "kızlar bir şey anlatacağım", "inanmayacaksınız ne oldu", "dün akşam ne oldu biliyor musunuz",
            "storyye bakın", "biri bana bunu açıklasın", "ayrılmışlar duydunuz mu", "{n} söyle onlara",
            "bugün bir şey oldu hala gülüyorum"
        ],
        reply: [
            "ne oldu", "anlat", "hadi ya", "ciddi misin", "yok artık", "ben demiştim", "kim kim",
            "inanmıyorum", "bekliyorum", "devam et", "sonra ne oldu", "çok normal", "ben zaten biliyordum",
            "sesli mesaj at", "telefonda anlatayım", "bunu yüz yüze konuşmamız lazım", "şok oldum",
            "{n} biliyor muydu", "kimseye söylemeyin", "of çok kötü", "iyi olmuş", "hak etti"
        ]
    },
    food: {
        w: 1.6,
        open: [
            "çok açım ne yesem", "yemek siparişi veriyorum isteyen", "şu kokoreççiyi denedik mi hiç",
            "yarın öğle yemeği nerede", "bugün mantı yaptım", "gece dürüm yiyen var mı", "kahve içmeye gidelim"
        ],
        reply: [
            "ben de", "dürüm", "pizza söyleyelim", "lahmacun", "burger olsun", "ben diyetteyim",
            "bana da söyle", "iskenderci", "çok güzel olmuş", "tarif at", "ben bu hafta çok yedim",
            "kahve şart", "starbucks mı", "yok kahve dünyası", "orası çok pahalı", "fiyatlar uçmuş",
            "geçen sefer çok beklettiler", "tamam söylüyorum", "ben tavuk dürüm", "acılı olsun"
        ]
    },
    football: {
        w: 1.3,
        open: [
            "maçı izleyen var mı", "bu akşam derbi var", "hakem yine rezaletti", "transfer haberini gördünüz mü",
            "maçı nerede izliyoruz", "bu sezon şampiyon oluruz"
        ],
        reply: [
            "izliyorum", "rezalet", "penaltı değildi", "gol", "GOOOOL", "bitti bu iş", "teknik direktör gitsin",
            "bu takımdan bir şey olmaz", "seneye bakarız", "{n} yine ağlıyor", "bizim kahvede izleriz",
            "3-1 biter", "kupa bizim", "hakem satılmış", "çok iyi oynadık", "ofsayt", "var'a gitmedi bile"
        ]
    },
    series: {
        w: 1.2,
        open: [
            "yeni sezon çıkmış", "dün gece hangi diziyi bitirdim tahmin edin", "film önerisi lazım",
            "bu dizi beni bitirdi", "sinemaya gidelim mi bu hafta", "spoiler vermeyin daha izlemedim"
        ],
        reply: [
            "hangisi", "ben de izliyorum", "final çok kötüydü", "spoiler verme", "bende izlemedim daha",
            "çok iyi", "ilk bölüm biraz yavaş", "sonradan açılıyor", "netflixte mi", "şifreni versene",
            "{n} izledin mi", "film gecesi yapalım", "ağladım", "o sahne efsaneydi", "ikinci sezon gelecek mi"
        ]
    },
    music: {
        w: 0.9,
        open: [
            "konser biletleri satışa çıkmış", "şu şarkıyı dinleyin", "festivale gidiyor muyuz bu yıl",
            "spotify wrapped geldi atın"
        ],
        reply: [
            "alalım", "bilet çok pahalı", "ben aldım bile", "kaç para", "gidiyoruz", "çok iyi şarkı",
            "döngüde dinliyorum", "playlist at", "{n} sen bilet aldın mı", "sahne önü alalım", "tükenmiş"
        ]
    },
    life: {
        w: 1.8,
        open: [
            "bugün çok yoruldum", "pazartesi sendromu", "kimse uyumuyor mu", "uyuyamıyorum", "günaydın",
            "bugün hava çok güzel", "trafik rezalet", "yağmur yağıyor şemsiye almayın sakın", "işten yeni çıktım",
            "evden çıkmak istemiyorum"
        ],
        reply: [
            "aynen", "bende", "geçmiş olsun", "uyu artık", "günaydın", "ben de uyuyamıyorum", "yarın erken kalkacağım",
            "kahve iç", "dinlen biraz", "aynı", "çok haklısın", "hava bozacakmış", "{n} sen nasılsın",
            "iyiyim sen", "idare ediyor", "yorgunum", "hafta sonu olsa", "biraz yürüyüşe çıktım", "of ya",
            "çok sıkıldım", "neler yapıyorsunuz"
        ]
    },
    meme: {
        w: 1.4,
        open: ["bakın", "buna bakın", "bu tam {n}", "bu reel bizim grup", "sabah bunu gördüm"],
        reply: [
            "bu tam sen", "{n} etiketliyorum", "tam biz", "ben bunu zaten atmıştım", "efsane", "kaydettim",
            "nereden buluyorsun bunları", "çok iyi", "tam olarak bu", "aynısı", "gerçek"
        ]
    },
    trip: {
        w: 0.8,
        open: [
            "yazın tatile gidelim artık", "kaş planı ne oldu", "bayramda bir yere gidelim mi",
            "ev tutalım mı 4 gün", "kamp yapalım bu sene"
        ],
        reply: [
            "kesin gidelim", "kaç gün", "bütçe ne kadar", "araba ile mi gideriz", "otobüs bileti baktım",
            "ben izin alabilirim", "ev buldum linki atıyorum", "çok güzel yer", "deniz olsun yeter",
            "çadır bende var", "ben ağustostan önce yokum", "{n} gelir mi", "tarih belirleyelim", "anket açalım"
        ]
    }
};

// Short reactions anyone can drop into any conversation
const SAMPLE_GENERIC = [
    "aynen", "evet", "hayır", "tamam", "tm", "olur", "bilmiyorum", "neden", "nasıl yani", "ne",
    "cidden mi", "valla", "yok artık", "hadi ya", "çok iyi", "süper", "harika", "of", "off",
    "bence de", "katılıyorum", "haklısın", "bakarız", "sonra konuşuruz", "okey", "tamamdır",
    "gördüm", "şimdi gördüm", "kusura bakmayın geç gördüm", "telefonu bırakmıştım", "anladım",
    "mantıklı", "iyi fikir", "neyse", "boşver", "olsun", "aaa", "ya", "yaa", "evet ya",
    "aynen öyle", "kesinlikle", "bilemedim", "emin değilim", "bir bakayım", "dur bakıyorum",
    "{n} ne diyorsun", "{n} cevap ver", "{n} neredesin", "{n} yine kayıp"
];

const SAMPLE_LINKS = [
    "https://www.instagram.com/reel/C8kQ2xLtR4p/", "https://youtu.be/dQw4w9WgXcQ",
    "https://www.tiktok.com/@kullanici/video/7351204411", "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC",
    "https://x.com/kullanici/status/1793344512", "https://maps.app.goo.gl/kadikoy-moda"
];

const SAMPLE_MEDIA = [
    "<görsel dahil edilmedi>", "<görsel dahil edilmedi>", "<görsel dahil edilmedi>", "<çıkartma dahil edilmedi>",
    "<GIF dahil edilmedi>", "<video dahil edilmedi>", "<ses dahil edilmedi>"
];

// Days with their own story: birthdays, holidays, the summer trip...
const SAMPLE_EVENTS = {
    "2025-02-14": { boost: 1.5, lines: [["Burak Şahin", "sevgililer günü kutlu olsun yalnızlar kulübü"], ["Mert Demir", "SKSKSKSKS kendimizi kutluyoruz"], ["Elif Kaya", "ben bu sene de kendime çiçek aldım 💐"]] },
    "2025-04-12": { boost: 2.2, lines: [["Zeynep Arslan", "İyi ki doğdun Elif! 🎉🎂 Nice mutlu yıllara ❤️"], ["Ahmet Yılmaz", "İyi ki doğdun Elif 🎂"], ["Mert Demir", "iyi ki doğdun elif yaşlandın artık 🎉"], ["Burak Şahin", "iyi ki doğdun 🎉🎉"], ["Deniz Çelik", "iyi ki doğdunnn elif 🥳"], ["Elif Kaya", "çok teşekkür ederim sizi seviyorummm ❤️❤️😭"]] },
    "2025-05-19": { boost: 1.4, lines: [["Ahmet Yılmaz", "19 Mayıs kutlu olsun 🇹🇷"], ["Zeynep Arslan", "Bugün tatil değil mi? Sahile inelim"]] },
    "2025-06-06": { boost: 1.8, lines: [["Zeynep Arslan", "Kurban Bayramınız kutlu olsun herkese 🙏"], ["Ahmet Yılmaz", "Sizin de bayramınız kutlu olsun"], ["Mert Demir", "bayram tatilinde nereye gidiyoruz"]] },
    "2025-07-18": { boost: 3.2, lines: [["Zeynep Arslan", "Kaş için ev kesinleşti! 24-29 Temmuz ✨"], ["Elif Kaya", "AAAAA ÇOK MUTLUYUM 😍😍"], ["Mert Demir", "KAŞ GELİYORUZ"], ["Burak Şahin", "araba bende kimse merak etmesin"]] },
    "2025-07-25": { boost: 2.6, lines: [["Elif Kaya", "deniz buz gibi ama çok güzel 🥹"], ["Burak Şahin", "<görsel dahil edilmedi>"], ["Mert Demir", "akşam balık yiyoruz kimse kaçmasın"]] },
    "2025-09-05": { boost: 2.4, lines: [["Deniz Çelik", "yarın sabah uçağım var 🥲 sizi çok özleyeceğim"], ["Zeynep Arslan", "Biz de seni çok özleyeceğiz Deniz! Erasmus'un çok güzel geçsin ❤️"], ["Elif Kaya", "ağlıyorum şu an 😭😭"], ["Mert Demir", "deniz gidince grubun iq seviyesi düşecek"], ["Ahmet Yılmaz", "İyi yolculuklar, varınca yaz"]] },
    "2025-10-14": { boost: 1.2, lines: [["Mert Demir", "deniz yaşıyor mu"], ["Elif Kaya", "storylerden yaşıyor 🙈"], ["Burak Şahin", "deniz grubu sessize aldı bence"]] },
    "2025-11-28": { boost: 2.8, lines: [["Deniz Çelik", "döndüm 🌍 kim nerede buluşalım"], ["Mert Demir", "DENİZ DÖNDÜ"], ["Elif Kaya", "AAAA HOŞ GELDİN 😍❤️"], ["Zeynep Arslan", "Hoş geldin! Bu akşam toplanıyoruz o zaman"]] },
    "2025-12-31": { boost: 2.6, lines: [["Ahmet Yılmaz", "Mutlu yıllar herkese! 🎉"], ["Zeynep Arslan", "Mutlu yıllar! 2026 hepimize güzel geçsin ✨"], ["Elif Kaya", "mutlu yıllarrr ❤️❤️🎉"], ["Mert Demir", "MUTLU YILLAR"], ["Burak Şahin", "mutlu yıllar 🎉"], ["Deniz Çelik", "mutlu yıllar 🥳"]] },
    "2026-01-12": { boost: 0.6, lines: [["Zeynep Arslan", "Final haftası başladı, iki hafta yokum 🙏"], ["Mert Demir", "kimse yok zaten"]] },
    "2026-03-20": { boost: 1.8, lines: [["Ahmet Yılmaz", "Ramazan Bayramınız kutlu olsun"], ["Zeynep Arslan", "Bayramınız kutlu olsun 🙏"], ["Elif Kaya", "bayramınız kutlu olsun ❤️"]] },
    "2026-04-12": { boost: 2.2, lines: [["Mert Demir", "iyi ki doğdun elif 🎉 bu sefer ilk ben yazdım"], ["Zeynep Arslan", "İyi ki doğdun canım ❤️🎂"], ["Burak Şahin", "iyi ki doğdun 🎉"], ["Deniz Çelik", "iyi ki doğdun 🥳🎂"], ["Ahmet Yılmaz", "İyi ki doğdun Elif 🎂"], ["Elif Kaya", "sizi çok seviyorum 😭❤️"]] },
    "2026-06-24": { boost: 2.4, lines: [["Ahmet Yılmaz", "Mezun olduk arkadaşlar 🎓"], ["Elif Kaya", "MEZUNUZ 😭😭🎓"], ["Mert Demir", "artık işsiziz SKSKSKSK"], ["Zeynep Arslan", "Kep atma fotoğraflarını gruba atın lütfen"]] },
    "2026-08-08": { boost: 2.8, lines: [["Burak Şahin", "bodrum planı kesin mi"], ["Zeynep Arslan", "Kesin! Ev 10-15 Ağustos ✨"], ["Mert Demir", "BODRUM"]] },
    "2026-09-14": { boost: 1.4, lines: [["Deniz Çelik", "yeni işimde ilk günüm 🙂"], ["Zeynep Arslan", "Kolay gelsin Deniz! 🙏"], ["Elif Kaya", "kolay gelsinnn ❤️"]] }
};

function generateSampleChat() {
    const rand = sampleRng(20260412);
    const pick = (arr) => arr[Math.floor(rand() * arr.length)];
    const chance = (p) => rand() < p;
    const pad = (n) => String(n).padStart(2, "0");
    const dayKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    const fmt = (d) => `[${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}]`;
    const weightedPick = (items, weightOf) => {
        const total = items.reduce((s, it) => s + weightOf(it), 0);
        let r = rand() * total;
        for (const it of items) {
            r -= weightOf(it);
            if (r <= 0) return it;
        }
        return items[items.length - 1];
    };
    // Poisson-ish count via exponential gaps
    const poisson = (lambda) => {
        let k = 0, p = Math.exp(-lambda), s = p, u = rand();
        while (u > s && k < 40) { k++; p *= lambda / k; s += p; }
        return k;
    };

    // Session start hours: quiet at dawn, peaks after lunch and late evening
    const HOUR_WEIGHTS = [4.2, 2.6, 1.3, 0.5, 0.2, 0.15, 0.35, 0.9, 1.6, 2.0, 2.4, 2.7, 3.3, 3.6, 3.0, 3.0, 3.2, 3.8, 4.0, 4.3, 4.9, 5.7, 6.1, 5.3];
    const hours = [...Array(24).keys()];

    const isAway = (m, date) => (m.away || []).some(([a, b]) => date >= a && date <= b);
    const memberWeight = (m, hour) => {
        let w = m.weight;
        if (hour < 5) w *= m.night;
        else if (hour < 10) w *= m.morning;
        return w;
    };

    const topicNames = Object.keys(SAMPLE_TOPICS);

    // Turns a phrase into something that sounds like that person typed it
    const style = (m, text, others) => {
        text = text.replace(/\{n\}/g, () => pick(others).first);
        if (chance(m.swear) && m.swears.length) text = chance(0.5) ? `${text} ${pick(m.swears)}` : `${pick(m.swears)} ${text}`;
        if (m.lower) {
            text = text.toLocaleLowerCase("tr");
            if (chance(0.12)) text = text.replace(/([aeıioöuü])$/, "$1$1$1");
        } else {
            text = text.charAt(0).toLocaleUpperCase("tr") + text.slice(1);
        }
        if (chance(m.punct) && !/[?!.]$/.test(text)) {
            text += /\b(mı|mi|mu|mü|ne|neden|nasıl|nerede|kaç|kim)\b/.test(text) ? "?" : (chance(0.5) ? "." : "!");
        }
        if (chance(m.caps)) text = text.toLocaleUpperCase("tr");
        if (chance(m.emoji)) {
            const e = pick(m.emojis);
            text += " " + (chance(0.35) ? e + e : e);
        }
        return text;
    };

    // Long, story-like message (mostly Zeynep)
    const longMessage = (m, topic, others) => {
        const parts = [pick(topic.reply), pick(SAMPLE_GENERIC), pick(topic.reply)];
        if (chance(0.5)) parts.push(pick(topic.open));
        return style(m, parts.join(", "), others);
    };

    const messages = [];
    const push = (date, sender, text) => messages.push({ t: date.getTime(), line: `${fmt(date)} ${sender}: ${text}` });

    for (let day = new Date(SAMPLE_START); day <= SAMPLE_END; day.setDate(day.getDate() + 1)) {
        const key = dayKey(day);
        const event = SAMPLE_EVENTS[key];
        const weekday = day.getDay();
        const month = day.getMonth();

        // How chatty the group is today
        let lambda = 3.0;
        if (weekday === 5 || weekday === 6) lambda *= 1.35;
        if (weekday === 0) lambda *= 1.1;
        if (month === 0 || month === 5) lambda *= 0.65;          // exam months
        if (month === 6 || month === 7) lambda *= 1.25;          // summer
        if (day.getFullYear() === 2026 && month >= 2) lambda *= 1.1; // group gets livelier after Deniz is back
        lambda *= 0.45 + rand() * 1.1;                           // some days are just quiet
        if (chance(0.04)) lambda = 0.3;                          // nearly dead day
        if (event) lambda *= event.boost;

        const present = SAMPLE_MEMBERS.filter(m => !isAway(m, day));

        // Event lines come first, mid-morning
        if (event) {
            let t = new Date(day);
            t.setHours(event.boost < 1 ? 9 : 10 + Math.floor(rand() * 3), Math.floor(rand() * 60), Math.floor(rand() * 60));
            event.lines.forEach(([sender, text]) => {
                push(t, sender, text);
                t = new Date(t.getTime() + (20 + rand() * 600) * 1000);
            });
        }

        const sessions = poisson(lambda);
        for (let s = 0; s < sessions; s++) {
            const startHour = weightedPick(hours, h => HOUR_WEIGHTS[(h + (weekday === 6 || weekday === 0 ? 23 : 0)) % 24]);
            let t = new Date(day);
            t.setHours(startHour, Math.floor(rand() * 60), Math.floor(rand() * 60));

            const awake = present.filter(m => memberWeight(m, startHour) > 0);
            const starter = weightedPick(awake, m => memberWeight(m, startHour) * m.starter);
            // 2-5 people join this conversation
            const pool = awake.filter(m => m !== starter);
            const joinCount = Math.min(pool.length, 1 + Math.floor(rand() * 4));
            const participants = [starter];
            while (participants.length < joinCount + 1) {
                const p = weightedPick(pool.filter(m => !participants.includes(m)), m => memberWeight(m, startHour));
                participants.push(p);
            }

            const topic = SAMPLE_TOPICS[weightedPick(topicNames, n => SAMPLE_TOPICS[n].w)];
            const length = 2 + Math.floor(-Math.log(1 - rand()) * 7);
            let sender = starter;
            const used = new Set();
            // Nobody repeats the same line within one conversation
            const fresh = (arr) => {
                let phrase = pick(arr);
                for (let tries = 0; tries < 4 && used.has(phrase); tries++) phrase = pick(arr);
                used.add(phrase);
                return phrase;
            };

            for (let i = 0; i < length; i++) {
                const others = SAMPLE_MEMBERS.filter(m => m !== sender);
                let text;
                if (i === 0) {
                    text = style(sender, pick(topic.open), others);
                    if (topic === SAMPLE_TOPICS.meme || chance(sender.link)) text += " " + pick(SAMPLE_LINKS);
                } else if (chance(sender.media)) {
                    text = "‎" + pick(SAMPLE_MEDIA);
                } else if (chance(0.12)) {
                    text = fresh(sender.laughs);
                } else if (sender.long && chance(sender.long)) {
                    text = longMessage(sender, topic, others);
                } else if (chance(sender.link * 0.5)) {
                    text = pick(SAMPLE_LINKS);
                } else {
                    text = style(sender, fresh(chance(0.62) ? topic.reply : SAMPLE_GENERIC), others);
                }
                if (chance(0.015)) text += " ‎<Bu mesaj düzenlendi.>";
                push(t, sender.name, text);

                // Next message: mostly seconds to a few minutes later, sometimes a longer pause
                const gap = chance(0.08) ? 600 + rand() * 1800 : 5 + -Math.log(1 - rand()) * 70;
                t = new Date(t.getTime() + gap * 1000);
                if (dayKey(t) !== key && t.getHours() >= 5) break;

                // Same person keeps typing, or someone else answers
                if (!chance(sender.burst)) {
                    const candidates = participants.filter(m => m !== sender);
                    sender = weightedPick(candidates, m => memberWeight(m, t.getHours()));
                }
            }
        }
    }

    messages.sort((a, b) => a.t - b.t);

    // Group is created the evening before the first conversation
    const first = new Date(SAMPLE_START);
    first.setDate(first.getDate() - 1);
    first.setHours(21, 42, 7);
    const header = [
        `${fmt(first)} ${SAMPLE_GROUP_NAME}: ‎Mert Demir grubu oluşturdu`,
        `${fmt(first)} ${SAMPLE_GROUP_NAME}: ‎Mesajlar ve aramalar uçtan uca şifrelidir. Bu sohbetin dışında bulunan hiç kimse, WhatsApp bile bunları okuyamaz ve dinleyemez.`
    ];
    return header.concat(messages.map(m => m.line)).join("\n");
}
