import api from "@/services/api";

export function downloadFile(fileDownloadLink: string, fileName: string): void {
    api.get(fileDownloadLink, {responseType: "blob"})
        .then((response) => {
            // create file link in browser's memory
            const href = URL.createObjectURL(response.data);
            // create "a" HTML element with href to file & click
            const link = document.createElement('a');
            link.href = href;
            link.setAttribute('download', fileName); //or any other extension
            document.body.appendChild(link);
            link.click();
            // clean up "a" element & remove ObjectURL
            document.body.removeChild(link);
            URL.revokeObjectURL(href);
        });
}