import networkx as nx

G = nx.DiGraph()


def add_data() -> None:
    # add entity
    G.add_node("equipment:press-01", type="Equipment", name="Press Machine 01", location="line-a")
    G.add_node("component:hydraulic-unit", type="Component", name="Hydraulic Unit")
    G.add_node("part:hydraulic-valve-b", type="Part", name="Hydraulic Valve B", status="available")
    G.add_node("part:hydraulic-valve-a", type="Part", name="Hydraulic Valve A", status="discontinued")

    # add relation
    G.add_edge("equipment:press-01", "component:hydraulic-unit", relation="has_component")
    G.add_edge("component:hydraulic-unit", "part:hydraulic-valve-a", relation="uses_part", status="active")
    G.add_edge("part:hydraulic-valve-a", "part:hydraulic-valve-b", relation="superseded_by")


# example query
def get_equipment_using_part(graph: nx.DiGraph, part_id: str) -> list[str]:
    equipment_ids = []
    for equipment_id, data in graph.nodes(data=True):
        if data.get("type") != "Equipment":
            continue

        for component_id in graph.successors(equipment_id):
            if graph.edges[equipment_id, component_id].get("relation") == "has_component" and graph.has_edge(
                component_id,
                part_id,
            ):
                if graph.edges[component_id, part_id].get("relation") == "uses_part":
                    equipment_ids.append(equipment_id)

    return equipment_ids


def main() -> None:
    add_data()
    equipment = get_equipment_using_part(G, "part:hydraulic-valve-a")
    print(f"equipment using hydraulic-valve-a: {equipment}")


if __name__ == "__main__":
    main()
