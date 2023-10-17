export default function format_bytes(size) {
    const power = 2 ** 10
    let n = 0
    const power_labels = {0: "", 1: "К", 2: "М", 3: "Г", 4: "Т"}
    while (size > power) {
        size /= power
        n += 1
    }
    return Math.round(size) + power_labels[n] + "Б"
}