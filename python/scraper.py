import argparse
import os.path as path
import json
from playwright.sync_api import sync_playwright


def extract_ui_tree(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Wait for the network to be idle to ensure the UI is fully rendered
        # page.wait_for_load_state("domcontentloaded")

        # Recursive JS function executed in the browser context
        ui_tree_json = page.evaluate("""() => {
    const parseNode = (element) => {

    
        if (!element) return null;
                                     
        const rect = element.getBoundingClientRect();

        //Readable Position----------------------------
        const x = rect.left + window.scrollX;
        const y = rect.top + window.scrollY;

        const pageWidth = document.documentElement.scrollWidth;
        const pageHeight = document.documentElement.scrollHeight;

        // Horizontal thirds
        let horiz;
        if (x < pageWidth / 3) horiz = "left";
        else if (x < (2 * pageWidth) / 3) horiz = "center";
        else horiz = "right";

        // Vertical thirds
        let vert;
        if (y < pageHeight / 3) vert = "top";
        else if (y < (2 * pageHeight) / 3) vert = "middle";
        else vert = "bottom";
        //---------------------------------------

        const innerText = element.innerText || "";
        // Construct the base properties of the current UI element
        const nodeData = {
            view: "desktop",
            tagName: element.tagName.toLowerCase(),
            id: element.id || null,
            className: element.className || null,
            role: element.getAttribute('role') || null,
            text: innerText.trim(),
            position : vert + "-" + horiz,
            size : { width: Math.round((rect.width/100)*2.54), height: Math.round((rect.height/100)*2.54) },
            visible : !!(element.offsetParent !== null && rect.width > 0 && rect.height > 0),
            color : getComputedStyle(element).color,
            children: []
        };

        // Recursively parse each child element to build the branch
        for (const child of element.children) {
            const childTree = parseNode(child);
            if (childTree) {
                nodeData.children.push(childTree);
            }
        }
        
        return nodeData;
    };

    // Start parsing from the body tag
    return parseNode(document.body);
}""")
        browser.close()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"height": 360, "width": 414})
        page.goto(url)

        # Wait for the network to be idle to ensure the UI is fully rendered
        # page.wait_for_load_state("domcontentloaded")

        # Recursive JS function executed in the browser context
        ui_tree_json2 = page.evaluate("""() => {
    const parseNode = (element) => {
        if (!element) return null;
        
        const rect = element.getBoundingClientRect();

                //Readable Position----------------------------
        const x = rect.left + window.scrollX;
        const y = rect.top + window.scrollY;

        const pageWidth = document.documentElement.scrollWidth;
        const pageHeight = document.documentElement.scrollHeight;

        // Horizontal thirds
        let horiz;
        if (x < pageWidth / 3) horiz = "left";
        else if (x < (2 * pageWidth) / 3) horiz = "center";
        else horiz = "right";

        // Vertical thirds
        let vert;
        if (y < pageHeight / 3) vert = "top";
        else if (y < (2 * pageHeight) / 3) vert = "middle";
        else vert = "bottom";
        //---------------------------------------
        
        const innerText = element.innerText || "";
        // Construct the base properties of the current UI element
        const nodeData = {
            view : "mobile",
            tagName: element.tagName.toLowerCase(),
            id: element.id || null,
            className: element.className || null,
            role: element.getAttribute('role') || null,
            text: innerText.trim(),
            visible : !!(element.offsetParent !== null && rect.width > 0 && rect.height > 0),
            position :vert + "-" + horiz,
            size :{ width: Math.round((rect.width/400)*2.54), height: Math.round((rect.height/400)*2.54) },
            color : getComputedStyle(element).color,
            children: []
        };

        // Recursively parse each child element to build the branch
        for (const child of element.children) {
            const childTree = parseNode(child);
            if (childTree) {
                nodeData.children.push(childTree);
            }
        }
        
        return nodeData;
    };

    // Start parsing from the body tag
    return parseNode(document.body);
}""")
        browser.close()

    resTree = dict()
    resTree["desktop"] = ui_tree_json
    resTree["mobile"] = ui_tree_json2

    return resTree


# Example Usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="For Scraping Website UI in Json, for desktop and mobile"
    )
    parser.add_argument(
        "url",
        help="url of the webpage"
    )

    args = parser.parse_args()

    target_url = args.url
    _, page = path.split(target_url)
    page, _ = path.splitext(page)

    tree = extract_ui_tree(target_url)
    # print(json.dumps(tree, indent=2))
    with open(f"data/website_snapshots/{page}.json", "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=4, ensure_ascii=False)
    print(f"✅ success\nresult : {page}.json is ready...")
