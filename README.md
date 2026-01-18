# ParaTikZ
A stupid simple python script to compile **standalone TikZ figures** in parallel **on Linux**. 

This is designed for large LaTeX projects where many TikZ figures are compiled independently and benefit from parallel execution.

## Features

- Parallel compilation of `standalone` TikZ figures
- Preserves directory structure between source and output
- Recompiles only modified figures
- Simple implementation, no external Python dependencies

## Requirements
- `GNU parallel`, install it on ArchLinux `sudo pacman -S parallel`
- `Python`
- `lualatex`, tested with `TexLive`

## Execution
```python
    python compileTikzParallel.py figs/src figs/out/out -j 8
```

