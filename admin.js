const DRAFT_KEY = "mill-bakery-site-draft";
const GITHUB_TOKEN_KEY = "mill-bakery-github-token";
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
  galleryTitle: document.getElementById("gallery-title-input"),
  galleryText: document.getElementById("gallery-text-input"),
  menuTitle: document.getElementById("menu-title-input"),
  menuText: document.getElementById("menu-text-input"),
};

const favoritesEditor = document.getElementById("favorites-editor");
const galleryEditor = document.getElementById("gallery-editor");
const menuEditor = document.getElementById("menu-editor");
const previewFrame = document.getElementById("site-preview-frame");
const cropperCanvas = document.getElementById("cropper-canvas");
const cropperContext = cropperCanvas.getContext("2d");
const logoPreviewCanvas = document.getElementById("logo-preview-canvas");
const logoPreviewContext = logoPreviewCanvas.getContext("2d");
const zoomInput = document.getElementById("crop-zoom");
const publishStatus = document.getElementById("publish-status");

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

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
    <div class="editor-item" data-index="${index}">
      <label>Badge<input type="text" data-favorite-field="badge" value="${escapeHtml(item.badge)}" /></label>
      <label>Title<input type="text" data-favorite-field="title" value="${escapeHtml(item.title)}" /></label>
      <label>Description<textarea rows="3" data-favorite-field="text">${escapeHtml(item.text)}</textarea></label>
    </div>
  `;
}

function assetTemplate(item, index, group) {
  return `
    <div class="editor-item asset-editor" data-index="${index}" data-group="${group}">
      <label>Title<input type="text" data-asset-field="title" value="${escapeHtml(item.title)}" /></label>
      <label>Description<textarea rows="3" data-asset-field="text">${escapeHtml(item.text)}</textarea></label>
      <label>Image Upload<input type="file" data-asset-field="file" accept="image/*" /></label>
      <img src="${item.image || "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="}" alt="" />
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
  fieldMap.galleryTitle.value = siteData.gallery.title;
  fieldMap.galleryText.value = siteData.gallery.text;
  fieldMap.menuTitle.value = siteData.menuGallery.title;
  fieldMap.menuText.value = siteData.menuGallery.text;

  favoritesEditor.innerHTML = siteData.favorites.map(favoriteTemplate).join("");
  galleryEditor.innerHTML = siteData.gallery.items.map((item, index) => assetTemplate(item, index, "gallery")).join("");
  menuEditor.innerHTML = siteData.menuGallery.items.map((item, index) => assetTemplate(item, index, "menuGallery")).join("");
  document.getElementById("github-token-input").value = window.localStorage.getItem(GITHUB_TOKEN_KEY) || "";
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
  siteData.gallery.title = fieldMap.galleryTitle.value.trim();
  siteData.gallery.text = fieldMap.galleryText.value.trim();
  siteData.menuGallery.title = fieldMap.menuTitle.value.trim();
  siteData.menuGallery.text = fieldMap.menuText.value.trim();

  document.querySelectorAll(".editor-item").forEach((item) => {
    const index = Number(item.dataset.index);
    const group = item.dataset.group;

    if (group === "gallery" || group === "menuGallery") {
      const targetGroup = siteData[group].items;
      targetGroup[index] = {
        ...targetGroup[index],
        title: item.querySelector('[data-asset-field="title"]').value.trim(),
        text: item.querySelector('[data-asset-field="text"]').value.trim(),
      };
      return;
    }

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

function getCropGeometry() {
  const img = cropState.image;
  const cropSize = 180;
  const cropX = (cropperCanvas.width - cropSize) / 2;
  const cropY = (cropperCanvas.height - cropSize) / 2;
  const baseScale = Math.min(cropperCanvas.width / img.width, cropperCanvas.height / img.height);
  const scale = baseScale * cropState.zoom;
  const drawWidth = img.width * scale;
  const drawHeight = img.height * scale;
  const drawX = (cropperCanvas.width - drawWidth) / 2 + cropState.offsetX;
  const drawY = (cropperCanvas.height - drawHeight) / 2 + cropState.offsetY;

  return {
    cropSize,
    cropX,
    cropY,
    drawWidth,
    drawHeight,
    drawX,
    drawY,
  };
}

function getTransparentLogoDataUrl(size = 512) {
  if (!cropState.image) {
    return "";
  }

  const { cropSize, cropX, cropY, drawWidth, drawHeight, drawX, drawY } = getCropGeometry();
  const exportCanvas = document.createElement("canvas");
  exportCanvas.width = size;
  exportCanvas.height = size;
  const exportContext = exportCanvas.getContext("2d");

  exportContext.drawImage(
    cropState.image,
    ((cropX - drawX) / drawWidth) * cropState.image.width,
    ((cropY - drawY) / drawHeight) * cropState.image.height,
    (cropSize / drawWidth) * cropState.image.width,
    (cropSize / drawHeight) * cropState.image.height,
    0,
    0,
    size,
    size
  );

  const imageData = exportContext.getImageData(0, 0, size, size);
  const { data } = imageData;
  for (let index = 0; index < data.length; index += 4) {
    const red = data[index];
    const green = data[index + 1];
    const blue = data[index + 2];

    if (red > 245 && green > 245 && blue > 245) {
      data[index + 3] = 0;
    } else if (red > 232 && green > 232 && blue > 232) {
      data[index + 3] = Math.max(0, 255 - ((red + green + blue) / 3 - 232) * 10);
    }
  }

  exportContext.putImageData(imageData, 0, 0);
  return exportCanvas.toDataURL("image/png");
}

function renderLogoPreview() {
  logoPreviewContext.clearRect(0, 0, logoPreviewCanvas.width, logoPreviewCanvas.height);
  const dataUrl = getTransparentLogoDataUrl(256);
  if (!dataUrl) {
    return;
  }

  const image = new Image();
  image.onload = () => {
    logoPreviewContext.drawImage(image, 0, 0, logoPreviewCanvas.width, logoPreviewCanvas.height);
  };
  image.src = dataUrl;
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

  const { cropSize, cropX, cropY, drawWidth, drawHeight, drawX, drawY } = getCropGeometry();

  cropperContext.drawImage(cropState.image, drawX, drawY, drawWidth, drawHeight);
  cropperContext.fillStyle = "rgba(67, 43, 32, 0.45)";
  cropperContext.fillRect(0, 0, cropperCanvas.width, cropperCanvas.height);
  cropperContext.clearRect(cropX, cropY, cropSize, cropSize);
  cropperContext.drawImage(cropState.image, drawX, drawY, drawWidth, drawHeight);
  cropperContext.strokeStyle = "#e4ab24";
  cropperContext.lineWidth = 3;
  cropperContext.strokeRect(cropX, cropY, cropSize, cropSize);

  renderLogoPreview();
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

async function handleAssetFileInput(input) {
  const [file] = input.files;
  if (!file) {
    return;
  }

  const dataUrl = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.readAsDataURL(file);
  });

  const container = input.closest(".asset-editor");
  const group = container.dataset.group;
  const index = Number(container.dataset.index);
  siteData[group].items[index].image = dataUrl;
  container.querySelector("img").src = dataUrl;
  updatePreview();
}

async function getFileSha(owner, repo, branch, path, token) {
  const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
    },
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Failed to read ${path}`);
  }

  const data = await response.json();
  return data.sha;
}

async function upsertFile(owner, repo, branch, path, contentBase64, token, message) {
  const sha = await getFileSha(owner, repo, branch, path, token);
  const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      branch,
      content: contentBase64,
      sha: sha || undefined,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to publish ${path}`);
  }
}

function dataUrlToBase64(dataUrl) {
  return dataUrl.split(",")[1];
}

function extensionForDataUrl(dataUrl) {
  if (dataUrl.startsWith("data:image/png")) {
    return "png";
  }
  if (dataUrl.startsWith("data:image/jpeg")) {
    return "jpg";
  }
  if (dataUrl.startsWith("data:image/webp")) {
    return "webp";
  }
  return "png";
}

async function publishToGitHub() {
  updateDataFromForm();

  const token = document.getElementById("github-token-input").value.trim();
  const owner = document.getElementById("github-owner-input").value.trim();
  const repo = document.getElementById("github-repo-input").value.trim();
  const branch = document.getElementById("github-branch-input").value.trim();

  if (!token || !owner || !repo || !branch) {
    publishStatus.textContent = "Token, owner, repo, and branch are all required.";
    return;
  }

  window.localStorage.setItem(GITHUB_TOKEN_KEY, token);
  publishStatus.textContent = "Publishing to GitHub...";

  try {
    const publishData = structuredClone(siteData);
    const uploads = [];

    if (publishData.business.logo.startsWith("data:")) {
      uploads.push({
        path: "assets/uploads/logo.png",
        content: dataUrlToBase64(publishData.business.logo),
      });
      publishData.business.logo = "assets/uploads/logo.png";
    }

    if (publishData.meta.favicon.startsWith("data:")) {
      uploads.push({
        path: "assets/uploads/favicon.png",
        content: dataUrlToBase64(publishData.meta.favicon),
      });
      publishData.meta.favicon = "assets/uploads/favicon.png";
    }

    for (const [section, items] of [
      ["gallery", publishData.gallery.items],
      ["menu", publishData.menuGallery.items],
    ]) {
      items.forEach((item, index) => {
        if (item.image.startsWith("data:")) {
          const extension = extensionForDataUrl(item.image);
          const path = `assets/uploads/${section}-${index + 1}.${extension}`;
          uploads.push({ path, content: dataUrlToBase64(item.image) });
          item.image = path;
        }
      });
    }

    for (const file of uploads) {
      await upsertFile(owner, repo, branch, file.path, file.content, token, `Update ${file.path}`);
    }

    const jsonBase64 = btoa(unescape(encodeURIComponent(JSON.stringify(publishData, null, 2))));
    await upsertFile(owner, repo, branch, "data/site-content.json", jsonBase64, token, "Update site content");

    publishStatus.textContent = "Published successfully. GitHub Pages should rebuild in a minute or two.";
    siteData = publishData;
    updatePreview();
  } catch (error) {
    publishStatus.textContent = error.message;
  }
}

function bindEvents() {
  Object.values(fieldMap).forEach((field) => {
    field.addEventListener("input", updatePreview);
  });

  favoritesEditor.addEventListener("input", updatePreview);
  galleryEditor.addEventListener("input", updatePreview);
  menuEditor.addEventListener("input", updatePreview);

  galleryEditor.addEventListener("change", (event) => {
    if (event.target.matches('[data-asset-field="file"]')) {
      handleAssetFileInput(event.target);
    }
  });

  menuEditor.addEventListener("change", (event) => {
    if (event.target.matches('[data-asset-field="file"]')) {
      handleAssetFileInput(event.target);
    }
  });

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

  document.getElementById("use-logo-button").addEventListener("click", () => {
    const logoDataUrl = getTransparentLogoDataUrl(512);
    if (!logoDataUrl) {
      return;
    }
    siteData.business.logo = logoDataUrl;
    siteData.meta.favicon = getTransparentLogoDataUrl(64);
    updatePreview();
  });

  document.getElementById("download-logo-button").addEventListener("click", () => {
    const dataUrl = getTransparentLogoDataUrl(512);
    if (!dataUrl) {
      return;
    }
    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = "mill-bakery-logo.png";
    link.click();
  });

  document.getElementById("download-favicon-button").addEventListener("click", () => {
    const dataUrl = getTransparentLogoDataUrl(64);
    if (!dataUrl) {
      return;
    }
    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = "mill-bakery-favicon.png";
    link.click();
  });

  document.getElementById("publish-button").addEventListener("click", publishToGitHub);
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
