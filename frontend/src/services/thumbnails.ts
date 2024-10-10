import axios from "axios";

export function getOriginImageURL(thumbImage: string): string {
    if (/_thumb_large\.[a-z]+$/.test(thumbImage)) {
        return thumbImage.replace("_thumb_large", "")
    }
    return thumbImage
}


export function getSmallThumbnail(image: string): string {
    const parts = image.split(".");
    console.log(parts)
    if (parts.length < 2) return image;
    const extension = parts.pop();
    return `${parts.join(".")}_thumb_large.${extension}`;
}


export async function hasSmallThumbnail(image: string): Promise<boolean> {
    const thumbImage = getSmallThumbnail(image)
    try {
        const resp = await axios.head(thumbImage)
        return resp.status === 200
    } catch {
        return false
    }
}
