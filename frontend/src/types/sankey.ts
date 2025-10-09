export interface GraphNode {
    name: string;
}

export interface GraphLink {
    source: string;
    target: string;
    value: number;
}

export interface GraphData {
    nodes: GraphNode[];
    links: GraphLink[];
}
