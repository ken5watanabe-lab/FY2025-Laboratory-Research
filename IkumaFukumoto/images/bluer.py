from PIL import Image
for i in [2, 3, 4]:
    file = f"/Users/ikuma-fukumoto/program/FY2025-Laboratory-Research/IkumaFukumoto/images/fig{i}.png"
    # モザイクをかける
    mosaic_size = 15
    img = Image.open(file)
    img = img.resize((img.size[0] // mosaic_size, img.size[1] // mosaic_size), Image.NEAREST)
    img = img.resize((img.size[0] * mosaic_size, img.size[1] * mosaic_size), Image.NEAREST)
img.save(f"/Users/ikuma-fukumoto/program/FY2025-Laboratory-Research/IkumaFukumoto/images/fig{i}_mosaic.png")
