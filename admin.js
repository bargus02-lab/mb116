const DRAFT_KEY = "mill-bakery-site-draft";
const defaultDataUrl = "data/site-content.json";

let siteData = null;
let cropState = {
  image: null,
  zoom: 1,
  offsetX: 0,
  offsetY: 0,
  dragActive: false,
  dragStartX: 0,
  dragStartY: 0,
};

const fieldMap = {
  businessName: document.getElementById("business-name"),
  phoneDisplay: document.getElementById("phone-display"),
  phoneLink: document.getElementById("phone-link"),
  addressLine1: document.getElementById("address-line1"),
  addressLine2: document.getElementById("address-line2"),
  hoursDisplay: document.getElementById("hours-display-input"),
  hoursNote: document.getElementById("hours-note-input"),
  directionsUrl: document.getElementById("directions-url"),
  mapEmbedUrl: document.getElementById("map-embed-url"),
  instagramUrl: document.getElementById("instagram-url"),
  heroEyebrow: document.getElementById("hero-eyebrow-input"),
  heroTitle: document.getElementById("hero-title-input"),
  heroText: document.getElementById("hero-text-input"),
  highlight1: document.getElementById("highlight-1"),
  highlight2: document.getElementById("highlight-2"),
  highlight3: document.getElementById("highlight-3"),
  badgeTitle: document.getElementById("badge-title"),
  badgeText: document.getElementById("badge-text"),
  aboutTitle: document.getElementById("about-title-input"),
  aboutCopy1: document.getElementById("about-copy-1-input"),
  aboutCopy2: document.getElementById("about-copy-2-input"),
  instagramTitle: document.getElementById("instagram-title-input"),
  instagramText: document.getElementById("instagram-text-input"),
  instagramButtonText: document.getElementById("instagram-button-text"),
  footerTagline: document.getElementById("footer-tagline-input"),
};

const favoritesEditor = document.getElementById("favorites-editor");
const previewFrame = document.getElementById("site-preview-frame");
const cropperCanvas = document.getElementById("cropper-canvas");
const cropperContext = cropperCanvas.getContext("2d");
const logoPreviewCanvas = document.getElementById("logo-preview-canvas");
const logoPreviewContext = logoPreviewCanvas.getContext("2d");
const zoomInput = document.getElementById("crop-zoom");

async function loadBaseData() {
  const response = await fetch(defaultDataUrl, { cache: "no-store" });
  const baseData = await response.json();

  try {
    const draft = window.localStorage.getItem(DRAFT_KEY);
    if (draft) {
      siteData = JSON.parse(draft);
      return;
    }
  } catch (_error) {
    // Ignore invalid drafts.
  }

  siteData = baseData;
}

function favoriteTemplate(item, index) {
  return `
    <div class="favorite-editor-item" data-index="${index}">
      <label>Badge<input type="text" data-favorite-field="badge" value="${item.badge.replace(/"/g, "&quot;")}" /></label>
      <label>Title<input type="text" data-favorite-field="title" value="${item.title.replace(/"/g, "&quot;")}" /></label>
      <label>Description<textarea rows="3" data-favorite-field="text">${item.text}</textarea></label>
    </div>
  `;
}

function populateForm() {
  fieldMap.businessName.value = siteData.business.name;
  fieldMap.phoneDisplay.value = siteData.business.phoneDisplay;
  fieldMap.phoneLink.value = siteData.business.phoneLink;
  fieldMap.addressLine1.value = siteData.business.addressLine1;
  fieldMap.addressLine2.value = siteData.business.addressLine2;
  fieldMap.hoursDisplay.value = siteData.business.hoursDisplay;
  fieldMap.hoursNote.value = siteData.business.hoursNote;
  fieldMap.directionsUrl.value = siteData.business.directionsUrl;
  fieldMap.mapEmbedUrl.value = siteData.business.mapEmbedUrl;
  fieldMap.instagramUrl.value = siteData.business.instagramUrl;
  fieldMap.heroEyebrow.value = siteData.hero.eyebrow;
  fieldMap.heroTitle.value = siteData.hero.title;
  fieldMap.heroText.value = siteData.hero.text;
  fieldMap.highlight1.value = siteData.hero.highlights[0];
  fieldMap.highlight2.value = siteData.hero.highlights[1];
  fieldMap.highlight3.value = siteData.hero.highlights[2];
  fieldMap.badgeTitle.value = siteData.hero.badgeTitle;
  fieldMap.badgeText.value = siteData.hero.badgeText;
  fieldMap.aboutTitle.value = siteData.about.title;
  fieldMap.aboutCopy1.value = siteData.about.paragraphs[0];
  fieldMap.aboutCopy2.value = siteData.about.paragraphs[1];
  fieldMap.instagramTitle.value = siteData.social.title;
  fieldMap.instagramText.value = siteData.social.text;
  fieldMap.instagramButtonText.value = siteData.social.buttonText;
  fieldMap.footerTagline.value = siteData.footer.tagline;

  favoritesEditor.innerHTML = siteData.favorites.map(favoriteTemplate).join("");
}

function updateDataFromForm() {
  siteData.business.name = fieldMap.businessName.value.trim();
  siteData.business.phoneDisplay = fieldMap.phoneDisplay.value.trim();
  siteData.business.phoneLink = fieldMap.phoneLink.value.trim();
  siteData.business.addressLine1 = fieldMap.addressLine1.value.trim();
  siteData.business.addressLine2 = fieldMap.addressLine2.value.trim();
  siteData.business.hoursDisplay = fieldMap.hoursDisplay.value.trim();
  siteData.business.hoursNote = fieldMap.hoursNote.value.trim();
  siteData.business.directionsUrl = fieldMap.directionsUrl.value.trim();
  siteData.business.mapEmbedUrl = fieldMap.mapEmbedUrl.value.trim();
  siteData.business.instagramUrl = fieldMap.instagramUrl.value.trim();
  siteData.hero.eyebrow = fieldMap.heroEyebrow.value.trim();
  siteData.hero.title = fieldMap.heroTitle.value.trim();
  siteData.hero.text = fieldMap.heroText.value.trim();
  siteData.hero.highlights = [
    fieldMap.highlight1.value.trim(),
    fieldMap.highlight2.value.trim(),
    fieldMap.highlight3.value.trim(),
  ];
  siteData.hero.badgeTitle = fieldMap.badgeTitle.value.trim();
  siteData.hero.badgeText = fieldMap.badgeText.value.trim();
  siteData.about.title = fieldMap.aboutTitle.value.trim();
  siteData.about.paragraphs = [
    fieldMap.aboutCopy1.value.trim(),
    fieldMap.aboutCopy2.value.trim(),
  ];
  siteData.social.title = fieldMap.instagramTitle.value.trim();
  siteData.social.text = fieldMap.instagramText.value.trim();
  siteData.social.buttonText = fieldMap.instagramButtonText.value.trim();
  siteData.footer.tagline = fieldMap.footerTagline.value.trim();

  document.querySelectorAll(".favorite-editor-item").forEach((item) => {
    const index = Number(item.dataset.index);
    siteData.favorites[index] = {
      badge: item.querySelector('[data-favorite-field="badge"]').value.trim(),
      title: item.querySelector('[data-favorite-field="title"]').value.trim(),
      text: item.querySelector('[data-favorite-field="text"]').value.trim(),
    };
  });
}

function updatePreview() {
  updateDataFromForm();
  window.localStorage.setItem(DRAFT_KEY, JSON.stringify(siteData, null, 2));

  previewFrame.contentWindow?.postMessage(
    { type: "mill-bakery-preview-update", payload: siteData },
    window.location.origin
  );
}

function downloadFile(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function drawCropper() {
  cropperContext.clearRect(0, 0, cropperCanvas.width, cropperCanvas.height);

  if (!cropState.image) {
    cropperContext.fillStyle = "rgba(182, 55, 46, 0.08)";
    cropperContext.fillRect(0, 0, cropperCanvas.width, cropperCanvas.height);
    cropperContext.fillStyle = "#6d5a4d";
    cropperContext.font = '600 18px "Work Sans"';
    cropperContext.fillText("Upload a logo image to start cropping.", 24, 44);
    return;
  }

  const img = cropState.image;
  const baseScale = Math.min(cropperCanvas.width / img.width, cropperCanvas.height / img.height);
  const scale = baseScale * cropState.zoom;
  const drawWidth = img.width * scale;
  const drawHeight = img.height * scale;
  const drawX = (cropperCanvas.width - drawWidth) / 2 + cropState.offsetX;
  const drawY = (cropperCanvas.height - drawHeight) / 2 + cropState.offsetY;

  cropperContext.drawImage(img, drawX, drawY, drawWidth, drawHeight);

  const size = 180;
  const cropX = (cropperCanvas.width - size) / 2;
  const cropY = (cropperCanvas.height - size) / 2;

  cropperContext.fillStyle = "rgba(67, 43, 32, 0.45)";
  cropperContext.fillRect(0, 0, cropperCanvas.width, cropperCanvas.height);
  cropperContext.clearRect(cropX, cropY, size, size);
  cropperContext.drawImage(img, drawX, drawY, drawWidth, drawHeight);
  cropperContext.strokeStyle = "#e4ab24";
  cropperContext.lineWidth = 3;
  cropperContext.strokeRect(cropX, cropY, size, size);

  logoPreviewContext.clearRect(0, 0, logoPreviewCanvas.width, logoPreviewCanvas.height);
  logoPreviewContext.drawImage(
    cropperCanvas,
    cropX,
    cropY,
    size,
    size,
    0,
    0,
    logoPreviewCanvas.width,
    logoPreviewCanvas.height
  );
}

function bindCropper() {
  cropperCanvas.addEventListener("pointerdown", (event) => {
    cropState.dragActive = true;
    cropState.dragStartX = event.clientX;
    cropState.dragStartY = event.clientY;
  });

  window.addEventListener("pointerup", () => {
    cropState.dragActive = false;
  });

  window.addEventListener("pointermove", (event) => {
    if (!cropState.dragActive) {
      return;
    }

    cropState.offsetX += event.clientX - cropState.dragStartX;
    cropState.offsetY += event.clientY - cropState.dragStartY;
    cropState.dragStartX = event.clientX;
    cropState.dragStartY = event.clientY;
    drawCropper();
  });

  zoomInput.addEventListener("input", () => {
    cropState.zoom = Number(zoomInput.value);
    drawCropper();
  });
}

function bindEvents() {
  Object.values(fieldMap).forEach((field) => {
    field.addEventListener("input", updatePreview);
  });

  favoritesEditor.addEventListener("input", updatePreview);

  document.getElementById("save-draft-button").addEventListener("click", () => {
    updatePreview();
    alert("Draft saved in this browser.");
  });

  document.getElementById("export-json-button").addEventListener("click", () => {
    updateDataFromForm();
    downloadFile("site-content.json", JSON.stringify(siteData, null, 2), "application/json");
  });

  document.getElementById("clear-draft-button").addEventListener("click", () => {
    window.localStorage.removeItem(DRAFT_KEY);
    window.location.reload();
  });

  document.getElementById("open-preview-button").addEventListener("click", () => {
    window.open("index.html?preview=draft", "_blank", "noopener");
  });

  document.getElementById("logo-upload").addEventListener("change", (event) => {
    const [file] = event.target.files;
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const image = new Image();
      image.onload = () => {
        cropState.image = image;
        cropState.zoom = 1;
        cropState.offsetX = 0;
        cropState.offsetY = 0;
        zoomInput.value = "1";
        drawCropper();
      };
      image.src = reader.result;
    };
    reader.readAsDataURL(file);
  });

  document.getElementById("download-logo-button").addEventListener("click", () => {
    const dataUrl = logoPreviewCanvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = "mill-bakery-logo.png";
    link.click();
  });
}

async function init() {
  await loadBaseData();
  populateForm();
  bindCropper();
  bindEvents();
  drawCropper();
  updatePreview();
}

init();
