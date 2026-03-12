/**
 * ECharts Server-Side SVG Renderer
 *
 * Reads a JSON ECharts option from stdin, renders it to SVG using
 * ECharts SSR mode (no browser required), and writes the SVG string
 * to stdout.
 *
 * Usage:
 *   echo '{"title":{"text":"Test"},...}' | node echart_ssr.js
 *
 * Accepts optional width/height via wrapper JSON:
 *   {"option": {...}, "width": 700, "height": 400}
 *
 * If the input JSON has an "option" key, it's treated as a wrapper.
 * Otherwise the entire JSON is treated as the ECharts option.
 */

/* global process */
const echarts = require("echarts");

const DEFAULT_WIDTH = 700;
const DEFAULT_HEIGHT = 400;

let inputData = "";

process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
	inputData += chunk;
});

process.stdin.on("end", () => {
	try {
		const parsed = JSON.parse(inputData);

		let option, width, height;
		if (parsed.option && typeof parsed.option === "object") {
			option = parsed.option;
			width = parsed.width || DEFAULT_WIDTH;
			height = parsed.height || DEFAULT_HEIGHT;
		} else {
			option = parsed;
			width = DEFAULT_WIDTH;
			height = DEFAULT_HEIGHT;
		}

		const chart = echarts.init(null, null, {
			renderer: "svg",
			ssr: true,
			width: width,
			height: height,
		});

		chart.setOption(option);
		const svg = chart.renderToSVGString();
		chart.dispose();

		process.stdout.write(svg);
	} catch (err) {
		process.stderr.write("ECharts SSR error: " + err.message + "\n");
		process.exit(1);
	}
});
