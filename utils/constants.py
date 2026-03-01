# bg_colors dictionary
BG_COLORS = {
    "Pitch Black": "#09090b",
    "Hacker Green": "#064e3b",
    "Midnight Blue": "#172554",
    "Retro Terminal": "#451a03",
    "Deep Purple": "#1e1030",
    "Ocean Depth": "#0c1929",
    "Charcoal": "#1a1a2e",
    "Matrix": "#001a00",
    "Warm Dark": "#1c1410",
}

# Character sets for image-to-ascii conversion
CHAR_SETS = {
    # ── Classic ──
    "Simple": " .:-=+*#%@",
    "Standard": " .:-=+*#%@",
    "Detailed": " .'-:_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[5Z3dph2XvP9bgU4Y8kWR~Q]XM",
    "Blocks": " ░▒▓█",
    # ── Density Gradients ──
    "Minimal": " .:*#",
    "Light": " .`'^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Dense": " .,:;+*?%S#@",
    "Ultra Dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Gradient 10": " .:-=+*%#@█",
    "Gradient 16": " .'`:,;_-~=+<>!?/\\|(){}[]#&@",
    # ── Artistic ──
    "Dots Only": " ·•●○◉◎",
    "Stars": " ✦✧★☆✪✫✬",
    "Arrows": " ←↑→↓↗↘↙↖⇐⇑⇒⇓",
    "Math Symbols": " +−×÷=≠<>≤≥±∞",
    "Music": " ♩♪♫♬♭♯",
    "Cards": " ♠♣♥♦",
    "Chess": " ♔♕♖♗♘♙♚♛♜♝♞♟",
    "Geometric": " ◇◆□■△▲▽▼○●",
    "Box Drawing": " ─│┌┐└┘├┤┬┴┼",
    "Braille": " ⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿",
    # ── Themed ──
    "Binary": " 01",
    "Hex": " 0123456789ABCDEF",
    "Numeric": " 0123456789",
    "Alpha Lower": " abcdefghijklmnopqrstuvwxyz",
    "Alpha Upper": " ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "Japanese Katakana": " ァアィイゥウェエォオカキクケコサシスセソタチツテトナニヌネノ",
    "CJK Strokes": " ㇀㇁㇂㇃㇄㇅㇆㇇㇈㇉",
    "Emoji Faces": " 😶😐🙂😊😀😃😁😆",
    "Shade Blocks": " ░▒▓█▄▀▌▐",
}
