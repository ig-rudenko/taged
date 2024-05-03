export default function format_bytes(size: number): string {
    const power: number = 2 ** 10
    let n: number = 0
    const powerLabels: Map<number, string> = new Map<number, string>([[0, ""], [1, "К"], [2, "М"], [3, "Г"], [4, "Т"]])
    while (size > power) {
        size /= power
        n += 1
    }
    return Math.round(size) + (<string>powerLabels.get(n)) + "Б"
}