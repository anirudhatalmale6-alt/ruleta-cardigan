from playwright.sync_api import sync_playwright
import time, pathlib

url = "file://" + str(pathlib.Path(__file__).parent / "index.html")
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={"width":390,"height":760}, device_scale_factor=3.0, is_mobile=True, has_touch=True)
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERR: "+str(e)))
    pg.goto(url); time.sleep(1.0)

    # chips are SVG now?
    n_chip_svg = pg.eval_on_selector_all("#chips .chip svg", "els=>els.length")
    print("chip count / svg chips:", pg.eval_on_selector_all("#chips .chip","e=>e.length"), "/", n_chip_svg)
    print("has conic anywhere in computed bg:", pg.eval_on_selector("#chips .chip","e=>getComputedStyle(e).backgroundImage"))

    # select the $10 chip, then tap number 17 to place a bet
    pg.eval_on_selector_all("#chips .chip", "els=>{for(const e of els){if(e.dataset.v=='10'){e.click();break;}}}")
    time.sleep(0.2)
    before = pg.inner_text("#bal")
    # tap a straight number tile
    pg.eval_on_selector_all(".tile.num", "els=>{for(const e of els){if(e.dataset.n=='17'){const r=e.getBoundingClientRect();e.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.left+r.width/2,clientY:r.top+r.height/2,bubbles:true}));e.dispatchEvent(new PointerEvent('pointerup',{clientX:r.left+r.width/2,clientY:r.top+r.height/2,bubbles:true}));break;}}}")
    time.sleep(0.3)
    after = pg.inner_text("#bal")
    stake_svgs = pg.eval_on_selector_all(".stake svg","els=>els.length")
    print("balance before/after bet:", before, "/", after, "| stake SVG tags:", stake_svgs)

    # scroll chips into view and screenshot the bottom (chips) - viewport only
    pg.eval_on_selector("#chips","e=>e.scrollIntoView({block:'center'})")
    time.sleep(0.3)
    pg.screenshot(path=str(pathlib.Path(__file__).parent/"ios_chips.png"))

    # speech priming present?
    primed = pg.evaluate("()=>typeof speechSynthesis!=='undefined'")
    print("speechSynthesis available in test browser:", primed)

    # rotate cycle sanity
    pg.set_viewport_size({"width":760,"height":390}); time.sleep(0.4)
    pg.set_viewport_size({"width":390,"height":760}); time.sleep(0.4)
    print("chips after rotate:", pg.eval_on_selector_all("#chips .chip svg","e=>e.length"))
    b.close()
print("JS ERRORS:", errs if errs else "none")
