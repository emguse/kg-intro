import networkx as nx

G = nx.DiGraph()


def add_data() -> None:
    # add entity
    G.add_node("product:api-v2", type="Product", name="API v2", status="stable")
    G.add_node("product:api-v1", type="Product", name="API v1", status="deprecated")
    G.add_node("customer:acme-corp", type="Customer", name="Acme Corp", plan="enterprise")

    # add relation
    G.add_edge("customer:acme-corp", "product:api-v1", relation="uses", status="stable")
    G.add_edge("product:api-v1", "product:api-v2", relation="superseded_by")


# example query
def get_customers_using_product(G: nx.DiGraph, product_id: str) -> list:
    return [n for n, d in G.nodes(data=True) if d.get("type") == "Customer" and G.has_edge(n, product_id)]


def main() -> None:
    add_data()
    customers = get_customers_using_product(G, "product:api-v1")
    print(f"using api-v1 customers: {customers}")


if __name__ == "__main__":
    main()
