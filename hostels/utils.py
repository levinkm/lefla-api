from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import RoomImages


def compressImageSave(images, images2, images3, images4, name):

    image_quality = 65

    i = Image.open(images)
    i = i.convert("RGB")
    thumb_io = BytesIO()
    i.save(thumb_io, format="JPEG", quality=image_quality)

    i2 = Image.open(images2)
    i2 = i2.convert("RGB")
    thumb_io2 = BytesIO()
    i.save(thumb_io2, format="JPEG", quality=image_quality)

    i3 = Image.open(images3)
    i3 = i3.convert("RGB")
    thumb_io3 = BytesIO()
    i.save(thumb_io3, format="JPEG", quality=image_quality)

    i4 = Image.open(images4)
    i4 = i4.convert("RGB")
    thumb_io4 = BytesIO()
    i.save(thumb_io4, format="JPEG", quality=image_quality)

    inmemory_uploaded_file = InMemoryUploadedFile(
        thumb_io, None, name + " img1.jpeg", "image/jpeg", thumb_io.tell(), None
    )
    inmemory_uploaded_file2 = InMemoryUploadedFile(
        thumb_io2, None, name + " img2.jpeg", "image/jpeg", thumb_io.tell(), None
    )
    inmemory_uploaded_file3 = InMemoryUploadedFile(
        thumb_io3, None, name + " img3.jpeg", "image/jpeg", thumb_io.tell(), None
    )
    inmemory_uploaded_file4 = InMemoryUploadedFile(
        thumb_io4, None, name + " img4.jpeg", "image/jpeg", thumb_io.tell(), None
    )
    imageCreate = RoomImages.objects.create(
        image_url_1=inmemory_uploaded_file,
        image_url_2=inmemory_uploaded_file2,
        image_url_3=inmemory_uploaded_file3,
        image_url_4=inmemory_uploaded_file4,
    )
    return imageCreate
