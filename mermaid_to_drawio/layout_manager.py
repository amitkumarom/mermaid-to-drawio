class LayoutManager:
    def __init__(self, x_gap=220, y_gap=80, x_offset=60, y_offset=60):
        self.x_gap = x_gap
        self.y_gap = y_gap
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.positions = {}
        self.node_counter = 0
        self.groups = {}
        self.group_bbox = {}
    
    def add_node(self, node_id):
        if node_id not in self.positions:
            row = self.node_counter % 20
            col = self.node_counter // 20
            x = self.x_offset + col * self.x_gap
            y = self.y_offset + row * self.y_gap
            self.positions[node_id] = (x, y)
            self.node_counter += 1
    
    def add_node_to_group(self, group_id, node_id, x, y, width, height):
        if not group_id:
            return
            
        if group_id not in self.groups:
            self.groups[group_id] = []
            
        self.groups[group_id].append(node_id)
        
        # Update group bounding box
        if group_id not in self.group_bbox:
            self.group_bbox[group_id] = [x, y, x + width, y + height]
        else:
            bbox = self.group_bbox[group_id]
            bbox[0] = min(bbox[0], x)
            bbox[1] = min(bbox[1], y)
            bbox[2] = max(bbox[2], x + width)
            bbox[3] = max(bbox[3], y + height)
    
    def get_position(self, node_id):
        return self.positions.get(node_id, (0, 0))
    
    def get_group_bbox(self, group_id):
        if group_id not in self.group_bbox:
            return None
            
        bbox = self.group_bbox[group_id]
        padding = 20
        return [
            bbox[0] - padding,
            bbox[1] - padding,
            bbox[2] - bbox[0] + 2 * padding,
            bbox[3] - bbox[1] + 2 * padding
        ]