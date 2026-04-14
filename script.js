const yearElement = document.getElementById("year");
const brandLogoCanvas = document.getElementById("brand-logo");

if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}

if (brandLogoCanvas) {
  const image = new Image();
  image.src = brandLogoCanvas.dataset.logoSrc;

  image.addEventListener("load", () => {
    const context = brandLogoCanvas.getContext("2d");

    if (!context) {
      return;
    }

    const crop = {
      x: 20,
      y: 250,
      width: 335,
      height: 390,
    };

    brandLogoCanvas.width = crop.width;
    brandLogoCanvas.height = crop.height;

    context.clearRect(0, 0, crop.width, crop.height);
    context.drawImage(
      image,
      crop.x,
      crop.y,
      crop.width,
      crop.height,
      0,
      0,
      crop.width,
      crop.height
    );

    const imageData = context.getImageData(0, 0, crop.width, crop.height);
    const { data } = imageData;

    for (let index = 0; index < data.length; index += 4) {
      const red = data[index];
      const green = data[index + 1];
      const blue = data[index + 2];

      if (red > 245 && green > 245 && blue > 245) {
        data[index + 3] = 0;
      } else if (red > 232 && green > 232 && blue > 232) {
        data[index + 3] = Math.max(0, 255 - ((red + green + blue) / 3 - 232) * 12);
      }
    }

    context.putImageData(imageData, 0, 0);
  });
}
