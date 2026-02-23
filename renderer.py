import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Use LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
})

def mpl_render(sketch, figsize=(5,5), filename=None, dpi=300):
    """
    Renders a hierarchical sketch (objects + groups).
    Circles are filled with white.
    """

    fig, ax = plt.subplots(figsize=figsize)

    def _draw(obj_list):
        for obj in obj_list:
            # Group
            if "objects" in obj:
                _draw(obj["objects"])
            else:
                if obj["type"] == "line":
                    # Handle linestyle - can be string or tuple for custom patterns
                    linestyle = obj.get("linestyle", "solid")
                    
                    # Check if it's a custom dash pattern (tuple/list)
                    if isinstance(linestyle, (tuple, list)):
                        # Custom dash pattern: pass directly to dashes parameter
                        ax.plot(
                            obj["x"], obj["y"],
                            color=obj.get("edgecolor", "black"),
                            linewidth=obj.get("lw", 1.0),
                            dashes=linestyle,  # Custom pattern
                            zorder=obj.get("l", 1)
                        )
                    else:
                        # Predefined string style
                        linestyle_map = {
                            "solid": "-",
                            "dashed": "--",
                            "dotted": ":",
                            "dashdot": "-."
                        }
                        mpl_linestyle = linestyle_map.get(linestyle, "-")
                        
                        ax.plot(
                            obj["x"], obj["y"],
                            color=obj.get("edgecolor", "black"),
                            linewidth=obj.get("lw", 1.0),
                            linestyle=mpl_linestyle,
                            zorder=obj.get("l", 1)
                        )
                elif obj["type"] == "circle":
                    facecolor = obj.get("facecolor", "white")
                    fill = True if facecolor != "none" else False
                    c = plt.Circle(
                        (obj["x"], obj["y"]),
                        obj["r"],
                        fill=fill,
                        facecolor=facecolor,
                        edgecolor=obj.get("edgecolor", "black"),
                        linewidth=obj.get("lw", 1.0),
                        zorder=obj.get("l", 2)
                    )
                    ax.add_patch(c)
                elif obj["type"] == "polygon":
                    facecolor = obj.get("facecolor", "white")
                    fill = True if facecolor != "none" else False
                    poly = plt.Polygon(
                        obj["points"],
                        closed=True,
                        fill=fill,
                        facecolor=facecolor,
                        edgecolor=obj.get("edgecolor", "black"),
                        linewidth=obj.get("lw", 1.0),
                        zorder=obj.get("l", 2)
                    )
                    ax.add_patch(poly)
                elif obj["type"] == "arc":
                    arc = patches.Arc(
                        (obj["x"], obj["y"]),
                        obj["width"],
                        obj["height"],
                        angle=obj["angle"],
                        theta1=obj["theta1"],
                        theta2=obj["theta2"],
                        color=obj.get("edgecolor", "black"),
                        linewidth=obj.get("lw", 1.0),
                        zorder=obj.get("l", 2)
                    )
                    ax.add_patch(arc)
                elif obj["type"] == "text":
                    ax.text(
                        obj["x"],
                        obj["y"],
                        obj["text"],
                        fontsize=obj.get("fontsize", 20),
                        ha=obj.get("ha", "center"),
                        va=obj.get("va", "center"),
                        rotation=obj.get("rotation", 0.0),
                        zorder=obj.get("l", 10),
                        color=obj.get("color", "black")
                    )

    _draw(sketch["objects"])
    ax.set_aspect("equal")
    ax.axis("off")
    if filename:
        plt.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.close() # Close to free memory
    else:
        plt.show()
