const yearElement = document.getElementById("year");
const draftQueryEnabled = new URLSearchParams(window.location.search).get("preview") === "draft";

const defaultContent = {
  meta: {
    title: "Mill Bakery | Santa Ana Bakery and Breakfast Burritos",
    description:
      "Mill Bakery in Santa Ana serves Mexican pastries, pan dulce, breakfast burritos, coffee, and fresh morning favorites.",
    favicon: "assets/logo-windmill.svg",
  },
  business: {
    name: "Mill Bakery",
    phoneDisplay: "(714) 540-7278",
    phoneLink: "+17145407278",
    addressLine1: "116 W MacArthur Blvd",
    addressLine2: "Santa Ana, CA 92707",
    directionsUrl: "https://maps.google.com/?q=116+W+MacArthur+Blvd+Santa+Ana+CA+92707",
    mapEmbedUrl:
      "https://www.google.com/maps?q=116+W+MacArthur+Blvd,+Santa+Ana,+CA+92707&z=15&output=embed",
    instagramUrl: "https://www.instagram.com/millbakery.oc/",
    hoursDisplay: "Daily: 5:00 AM - 12:00 PM",
    hoursNote: "Hours based on current public listings and may change.",
    logo: "assets/logo-windmill.svg",
  },
  hero: {
    eyebrow: "Santa Ana bakery and breakfast stop",
    title: "Fresh pan dulce, breakfast burritos, and coffee every morning",
    text:
      "A neighborhood bakery on MacArthur serving Mexican pastries, conchas, burritos, coffee, and quick breakfast favorites for busy mornings.",
    highlights: [
      "Fresh pastries daily",
      "Known for breakfast burritos",
      "Easy pickup on MacArthur",
    ],
    badgeTitle: "Warm mornings start here",
    badgeText:
      "Inspired by the bakery card: cream background, bakery red, and a golden border feel with a simple local look.",
  },
  about: {
    title: "A local Santa Ana spot for pastries, coffee, and breakfast",
    paragraphs: [
      "Mill Bakery is a casual neighborhood bakery near MacArthur in Santa Ana, known for Mexican pastries, pan dulce, fresh coffee, and popular breakfast burritos.",
      "It is the kind of place people stop into early, pick up something warm, and head back to work or home with a box of favorites.",
    ],
  },
  favorites: [
    {
      badge: "Sweet bread",
      title: "Conchas",
      text: "Soft, fluffy, and fresh for the morning pastry run or an afternoon treat.",
    },
    {
      badge: "Bakery classic",
      title: "Pan dulce",
      text: "A colorful pastry case with classic Mexican bakery favorites and familiar daily staples.",
    },
    {
      badge: "Local standout",
      title: "Breakfast burritos",
      text: "A go-to order for regulars looking for a filling breakfast that is quick, hot, and easy to grab.",
    },
    {
      badge: "Morning essential",
      title: "Coffee",
      text: "Hot coffee that pairs naturally with pan dulce and a quick stop before the day starts.",
    },
  ],
  social: {
    title: "Follow along for fresh bakes and daily bakery updates",
    text:
      "See what is coming out of the pastry case, keep up with breakfast favorites, and follow the bakery on Instagram.",
    buttonText: "Follow @millbakery.oc",
  },
  footer: {
    tagline: "Mexican pastries, breakfast burritos, coffee, and pan dulce.",
  },
  gallery: {
    title: "A quick look inside Mill Bakery",
    text: "Fresh pastry trays, coffee, and the bakery counter all in one place.",
    items: [
      {
        title: "Pastry Counter",
        text: "Upload an interior or pastry-case photo here.",
        image: "",
      },
      {
        title: "Morning Coffee",
        text: "Show coffee service, burritos, or a breakfast setup.",
        image: "",
      },
      {
        title: "Fresh Bakes",
        text: "Use this slot for conchas, pan dulce, or daily specials.",
        image: "",
      },
    ],
  },
  menuGallery: {
    title: "Upload menu snapshots or specialty boards",
    text: "This section is built for quick image updates whenever the menu changes.",
    items: [
      {
        title: "Menu Board",
        text: "Add a photo of a printed menu or counter board.",
        image: "",
      },
      {
        title: "Breakfast Specials",
        text: "Use this for burrito specials, combo boards, or promos.",
        image: "",
      },
      {
        title: "Seasonal Items",
        text: "Swap in any limited-run pastries or featured drinks.",
        image: "",
      },
    ],
  },
};

function deepMerge(base, override) {
  if (Array.isArray(base) && Array.isArray(override)) {
    return override;
  }

  if (
    base &&
    override &&
    typeof base === "object" &&
    typeof override === "object" &&
    !Array.isArray(base) &&
    !Array.isArray(override)
  ) {
    const merged = { ...base };

    for (const key of Object.keys(override)) {
      merged[key] = deepMerge(base[key], override[key]);
    }

    return merged;
  }

  return override ?? base;
}

function setText(id, value) {
  const element = document.getElementById(id);

  if (element) {
    element.textContent = value ?? "";
  }
}

function setLink(id, href, text) {
  const element = document.getElementById(id);

  if (element) {
    element.href = href;

    if (typeof text === "string") {
      element.textContent = text;
    }
  }
}

function renderList(id, items) {
  const list = document.getElementById(id);

  if (!list) {
    return;
  }

  list.innerHTML = "";

  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  }
}

function renderFavorites(items) {
  const grid = document.getElementById("favorites-grid");

  if (!grid) {
    return;
  }

  grid.innerHTML = "";

  for (const item of items) {
    const article = document.createElement("article");
    article.className = "item-card";

    article.innerHTML = `
      <span class="item-badge"></span>
      <h3></h3>
      <p></p>
    `;

    article.querySelector(".item-badge").textContent = item.badge;
    article.querySelector("h3").textContent = item.title;
    article.querySelector("p").textContent = item.text;

    grid.appendChild(article);
  }
}

function renderImageCards(id, items) {
  const grid = document.getElementById(id);

  if (!grid) {
    return;
  }

  grid.innerHTML = "";

  for (const item of items) {
    const figure = document.createElement("figure");
    figure.className = "image-card";

    if (!item.image) {
      figure.classList.add("is-empty");
    }

    figure.innerHTML = `
      <div class="image-placeholder">Photo Placeholder</div>
      <img alt="" />
      <figcaption>
        <h3></h3>
        <p></p>
      </figcaption>
    `;

    const image = figure.querySelector("img");
    image.src = item.image || "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
    image.alt = item.title;

    figure.querySelector("h3").textContent = item.title;
    figure.querySelector("p").textContent = item.text;

    grid.appendChild(figure);
  }
}

function applySiteContent(content) {
  document.title = content.meta.title;

  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute("content", content.meta.description);
  }

  const favicon = document.querySelector('link[rel="icon"]');
  if (favicon) {
    favicon.setAttribute("href", content.meta.favicon);
  }

  const logo = document.getElementById("brand-logo-image");
  if (logo) {
    logo.src = content.business.logo;
  }

  setText("brand-name", content.business.name);
  setText("hero-eyebrow", content.hero.eyebrow);
  setText("hero-title", content.hero.title);
  setText("hero-text", content.hero.text);
  renderList("hero-highlights", content.hero.highlights);
  setText("hero-badge-label", content.business.name);
  setText("hero-badge-title", content.hero.badgeTitle);
  setText("hero-badge-text", content.hero.badgeText);
  setText("hero-stat-address", content.business.addressLine1);
  setText("hero-stat-phone", content.business.phoneDisplay);
  setText("hero-stat-hours", content.business.hoursDisplay.replace("Daily: ", ""));

  setLink("call-now-link", `tel:${content.business.phoneLink}`);
  setLink("directions-link", content.business.directionsUrl);
  setLink("open-maps-link", content.business.directionsUrl);

  setText("about-title", content.about.title);
  setText("about-copy-1", content.about.paragraphs[0]);
  setText("about-copy-2", content.about.paragraphs[1]);

  renderFavorites(content.favorites);
  setText("gallery-title", content.gallery.title);
  setText("gallery-text", content.gallery.text);
  renderImageCards("gallery-grid", content.gallery.items);
  setText("menu-title", content.menuGallery.title);
  setText("menu-text", content.menuGallery.text);
  renderImageCards("menu-grid", content.menuGallery.items);

  setText("visit-title", "Find the bakery, check hours, and stop by early");
  setText("address-line-1", content.business.addressLine1);
  setText("address-line-2", content.business.addressLine2);
  setLink("phone-link", `tel:${content.business.phoneLink}`, content.business.phoneDisplay);
  setText("phone-help-text", "Tap to call for bakery questions or quick directions.");
  setText("hours-display", content.business.hoursDisplay);
  setText("hours-note", content.business.hoursNote);

  const mapFrame = document.getElementById("map-frame");
  if (mapFrame) {
    mapFrame.src = content.business.mapEmbedUrl;
  }

  setText("instagram-title", content.social.title);
  setText("instagram-text", content.social.text);
  setLink("instagram-link", content.business.instagramUrl, content.social.buttonText);

  setText("footer-brand", content.business.name);
  setText("footer-tagline", content.footer.tagline);
  setLink("footer-phone", `tel:${content.business.phoneLink}`, content.business.phoneDisplay);
  setText("footer-address", `${content.business.addressLine1}, ${content.business.addressLine2}`);

  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
}

async function loadSiteContent() {
  let data = defaultContent;

  try {
    const response = await fetch("data/site-content.json", { cache: "no-store" });

    if (response.ok) {
      const remoteData = await response.json();
      data = deepMerge(defaultContent, remoteData);
    }
  } catch (_error) {
    data = defaultContent;
  }

  if (draftQueryEnabled) {
    try {
      const draft = window.localStorage.getItem("mill-bakery-site-draft");

      if (draft) {
        data = deepMerge(data, JSON.parse(draft));
      }
    } catch (_error) {
      // Ignore invalid local drafts.
    }
  }

  applySiteContent(data);
}

window.addEventListener("message", (event) => {
  if (event.data?.type === "mill-bakery-preview-update" && event.data.payload) {
    const merged = deepMerge(defaultContent, event.data.payload);
    applySiteContent(merged);
  }
});

loadSiteContent();
