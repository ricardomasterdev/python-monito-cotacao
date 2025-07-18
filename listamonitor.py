from screeninfo import get_monitors

for m in get_monitors():
    print(f"Monitor {m.name}: x={m.x}, y={m.y}, {m.width}×{m.height}")