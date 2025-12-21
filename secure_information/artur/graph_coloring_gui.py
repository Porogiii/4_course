import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
from typing import Dict, List, Tuple, Optional
import threading
import time

from graph_coloring_zkp import (
    Graph, GraphColoringSolver, GraphColoringZKProtocol, 
    Color, Edge
)


class GraphVisualization:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.vertex_positions = {}
        self.vertex_radius = 25
        self.color_map = {
            Color.RED: '#FF4444',
            Color.BLUE: '#4444FF', 
            Color.GREEN: '#44FF44',
            Color.YELLOW: '#FFFF44',
            Color.PURPLE: '#FF44FF',
            Color.ORANGE: '#FF8844'
        }
        self.default_vertex_color = '#CCCCCC'
        self.edge_color = '#666666'
        self.highlighted_edge_color = '#FF0000'
        self.highlighted_edge_width = 4
        self.normal_edge_width = 2
    
    def calculate_positions(self, num_vertices: int, canvas_width: int, canvas_height: int):
        self.vertex_positions = {}
        if num_vertices == 0:
            return
        
        margin = 60
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        if num_vertices == 1:
            self.vertex_positions[0] = (center_x, center_y)
        elif num_vertices == 2:
            self.vertex_positions[0] = (center_x - 50, center_y)
            self.vertex_positions[1] = (center_x + 50, center_y)
        else:
            radius = min(canvas_width, canvas_height) // 2 - margin
            for i in range(num_vertices):
                angle = 2 * math.pi * i / num_vertices - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.vertex_positions[i] = (x, y)
    
    def draw_graph(self, graph: Graph, coloring: Optional[Dict[int, Color]] = None, 
                   highlighted_edge: Optional[Edge] = None):
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.canvas.after(100, lambda: self.draw_graph(graph, coloring, highlighted_edge))
            return
        
        self.calculate_positions(graph.num_vertices, canvas_width, canvas_height)
        
        for edge in graph.edges:
            if edge.u in self.vertex_positions and edge.v in self.vertex_positions:
                x1, y1 = self.vertex_positions[edge.u]
                x2, y2 = self.vertex_positions[edge.v]
                
                if highlighted_edge and edge == highlighted_edge:
                    color = self.highlighted_edge_color
                    width = self.highlighted_edge_width
                else:
                    color = self.edge_color
                    width = self.normal_edge_width
                
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags="edge")
        
        for vertex in range(graph.num_vertices):
            if vertex in self.vertex_positions:
                x, y = self.vertex_positions[vertex]
                
                if coloring and vertex in coloring:
                    fill_color = self.color_map.get(coloring[vertex], self.default_vertex_color)
                else:
                    fill_color = self.default_vertex_color
                
                self.canvas.create_oval(
                    x - self.vertex_radius, y - self.vertex_radius,
                    x + self.vertex_radius, y + self.vertex_radius,
                    fill=fill_color, outline='black', width=2, tags="vertex"
                )
                
                self.canvas.create_text(
                    x, y, text=str(vertex + 1), font=('Arial', 12, 'bold'),
                    fill='black', tags="vertex_label"
                )


class ZKProtocolGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Протокол ZK для раскраски графа")
        self.root.geometry("1000x700")
        
        self.graph: Optional[Graph] = None
        self.coloring: Optional[Dict[int, Color]] = None
        self.protocol: Optional[GraphColoringZKProtocol] = None
        self.current_round = 0
        self.protocol_running = False
        
        self.graph_viz: Optional[GraphVisualization] = None
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.create_control_panel(main_frame)
        self.create_graph_panel(main_frame)
        self.create_log_panel(main_frame)
    
    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Управление", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        info_frame = ttk.LabelFrame(control_frame, text="Информация", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.graph_info_label = ttk.Label(info_frame, text="Граф не загружен")
        self.graph_info_label.pack()
        
        self.coloring_info_label = ttk.Label(info_frame, text="")
        self.coloring_info_label.pack()
        
        load_frame = ttk.LabelFrame(control_frame, text="Загрузка", padding="5")
        load_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(load_frame, text="Загрузить файл", 
                  command=self.load_graph_file).pack(fill=tk.X, pady=2)
        
        protocol_frame = ttk.LabelFrame(control_frame, text="Протокол", padding="5")
        protocol_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(protocol_frame, text="Раундов:").pack()
        self.rounds_var = tk.StringVar(value="10")
        ttk.Spinbox(protocol_frame, from_=1, to=50, textvariable=self.rounds_var, width=10).pack(pady=2)
        
        self.auto_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(protocol_frame, text="Авто режим", 
                       variable=self.auto_mode_var).pack(pady=2)
        
        ttk.Label(protocol_frame, text="Задержка (сек):").pack()
        self.delay_var = tk.StringVar(value="1.0")
        ttk.Spinbox(protocol_frame, from_=0.1, to=5.0, increment=0.1, 
                   textvariable=self.delay_var, width=10).pack(pady=2)
        
        buttons_frame = ttk.LabelFrame(control_frame, text="Управление", padding="5")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(buttons_frame, text="Запустить",
                                      command=self.start_protocol, state='disabled')
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.step_button = ttk.Button(buttons_frame, text="Шаг",
                                     command=self.next_step, state='disabled')
        self.step_button.pack(fill=tk.X, pady=2)
        
        self.reset_button = ttk.Button(buttons_frame, text="Сброс",
                                      command=self.reset_protocol, state='disabled')
        self.reset_button.pack(fill=tk.X, pady=2)
        
        status_frame = ttk.LabelFrame(control_frame, text="Статус", padding="5")
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Готов")
        self.status_label.pack()
        
        self.round_label = ttk.Label(status_frame, text="")
        self.round_label.pack()
    
    def create_graph_panel(self, parent):
        graph_frame = ttk.LabelFrame(parent, text="Граф", padding="10")
        graph_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.graph_canvas = tk.Canvas(graph_frame, width=500, height=400, bg='white')
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.graph_viz = GraphVisualization(self.graph_canvas)
    
    def create_log_panel(self, parent):
        log_frame = ttk.LabelFrame(parent, text="Лог", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_graph_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с графом",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if filename:
            self.load_graph_from_file(filename)
    
    def load_graph_from_file(self, filename: str):
        try:
            self.log(f"Загрузка графа из {filename}...")
            
            self.graph, file_coloring = Graph.from_file(filename)
            self.log(f"Граф: {self.graph.num_vertices} вершин, {len(self.graph.edges)} рёбер")
            
            if file_coloring:
                self.coloring = file_coloring
                self.log("Раскраска загружена из файла")
            else:
                solver = GraphColoringSolver(self.graph)
                self.coloring = solver.find_minimal_coloring()
                
                if not self.coloring:
                    self.log("Не удалось найти раскраску")
                    messagebox.showerror("Ошибка", "Не удалось найти раскраску")
                    return
            
            colors_used = set(self.coloring.values())
            self.log(f"Раскраска использует {len(colors_used)} цветов")
            
            for vertex, color in sorted(self.coloring.items()):
                self.log(f"  Вершина {vertex + 1}: {color.name}")
            
            self.update_graph_info()
            self.draw_current_graph()
            
            self.start_button.config(state='normal')
            self.reset_protocol()
            
        except Exception as e:
            error_msg = f"Ошибка: {e}"
            self.log(error_msg)
            messagebox.showerror("Ошибка", error_msg)
    
    def update_graph_info(self):
        if self.graph and self.coloring:
            colors_used = len(set(self.coloring.values()))
            self.graph_info_label.config(
                text=f"Вершин: {self.graph.num_vertices}, Рёбер: {len(self.graph.edges)}"
            )
            self.coloring_info_label.config(
                text=f"Цветов: {colors_used}"
            )
        else:
            self.graph_info_label.config(text="Граф не загружен")
            self.coloring_info_label.config(text="")
    
    def draw_current_graph(self, highlighted_edge: Optional[Edge] = None):
        if self.graph and self.graph_viz:
            coloring_to_show = None if self.protocol_running else self.coloring
            self.graph_viz.draw_graph(self.graph, coloring_to_show, highlighted_edge)
    
    def start_protocol(self):
        if not self.graph or not self.coloring:
            messagebox.showerror("Ошибка", "Загрузите граф")
            return
        
        try:
            num_rounds = int(self.rounds_var.get())
            self.auto_mode = self.auto_mode_var.get()
            
            self.protocol = GraphColoringZKProtocol(self.graph, self.coloring)
            self.current_round = 0
            self.protocol_running = True
            
            self.start_button.config(state='disabled')
            self.step_button.config(state='normal' if not self.auto_mode else 'disabled')
            self.reset_button.config(state='normal')
            
            self.draw_current_graph()
            
            self.log(f"ПРОТОКОЛ ZK ЗАПУЩЕН")
            self.log(f"Граф: {self.graph.num_vertices} вершин, {len(self.graph.edges)} рёбер")
            self.log(f"Раундов: {num_rounds}")
            
            self.update_status("Запущен", 0, num_rounds)
            
            if self.auto_mode:
                self.run_auto_protocol(num_rounds)
            else:
                self.log("Нажмите 'Шаг' для выполнения")
                
        except Exception as e:
            self.log(f"Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))
    
    def run_auto_protocol(self, num_rounds: int):
        def run_rounds():
            try:
                delay = float(self.delay_var.get())
                
                for round_num in range(1, num_rounds + 1):
                    if not self.protocol_running:
                        break
                    
                    self.root.after(0, lambda r=round_num: self.execute_round(r))
                    time.sleep(delay)
                
                if self.protocol_running:
                    self.root.after(0, self.finish_protocol)
                    
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Ошибка: {e}"))
        
        threading.Thread(target=run_rounds, daemon=True).start()
    
    def next_step(self):
        if not self.protocol_running or not self.protocol:
            return
        
        num_rounds = int(self.rounds_var.get())
        self.current_round += 1
        
        if self.current_round <= num_rounds:
            self.execute_round(self.current_round)
            
            if self.current_round >= num_rounds:
                self.finish_protocol()
        else:
            self.finish_protocol()
    
    def execute_round(self, round_num: int):
        try:
            self.log(f"\n--- РАУНД {round_num} ---")
            
            commitments = self.protocol.prover.start_round()
            self.protocol.verifier.receive_commitments(commitments)
            
            challenge_edge = self.protocol.verifier.generate_challenge()
            self.log(f"Ребро: ({challenge_edge.u + 1}, {challenge_edge.v + 1})")
            
            self.draw_current_graph(challenge_edge)
            
            color_u, color_v, nonce_u, nonce_v = self.protocol.prover.respond_to_challenge(challenge_edge)
            self.log(f"Цвета: {color_u.name}, {color_v.name}")
            
            is_valid = self.protocol.verifier.verify_response(challenge_edge, color_u, color_v, nonce_u, nonce_v)
            
            # Добавляем результат в лог протокола
            self.protocol.protocol_log.append({
                'round': round_num,
                'challenged_edge': (challenge_edge.u + 1, challenge_edge.v + 1),
                'valid': is_valid
            })
            
            if is_valid:
                self.log("✅ Успех")
            else:
                self.log("❌ Провал")
                self.protocol_running = False
                self.update_status("Провален", round_num, int(self.rounds_var.get()))
                return
            
            num_rounds = int(self.rounds_var.get())
            self.update_status("Выполняется", round_num, num_rounds)
            
        except Exception as e:
            self.log(f"Ошибка: {e}")
            self.protocol_running = False
    
    def finish_protocol(self):
        if not self.protocol:
            return
        
        self.protocol_running = False
        num_rounds = int(self.rounds_var.get())
        
        stats = self.protocol.get_protocol_statistics()
        
        if stats['success_rate'] == 1.0:
            self.log(f"\n✅ ПРОТОКОЛ ЗАВЕРШЕН УСПЕШНО")
            self.log(f"Все {stats['successful_rounds']} раундов пройдены")
            self.update_status("Успех", num_rounds, num_rounds)
        else:
            self.log(f"\n❌ ПРОТОКОЛ ПРОВАЛЕН")
            self.update_status("Провален", stats['successful_rounds'], num_rounds)
        
        self.log(f"Статистика:")
        self.log(f"  Раундов: {stats['total_rounds']}")
        self.log(f"  Успешных: {stats['successful_rounds']}")
        self.log(f"  Безопасность: {stats['security_level']:.2e}")
        
        self.draw_current_graph()
        
        self.start_button.config(state='normal')
        self.step_button.config(state='disabled')
    
    def reset_protocol(self):
        self.protocol_running = False
        self.protocol = None
        self.current_round = 0
        
        if self.graph and self.coloring:
            self.start_button.config(state='normal')
        self.step_button.config(state='disabled')
        self.reset_button.config(state='disabled')
        
        self.draw_current_graph()
        self.update_status("Готов", 0, 0)
        self.log("Сброс")
    
    def update_status(self, status: str, current_round: int, total_rounds: int):
        self.status_label.config(text=status)
        
        if total_rounds > 0:
            self.round_label.config(text=f"Раунд: {current_round}/{total_rounds}")
        else:
            self.round_label.config(text="")
    
    def log(self, message: str):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = ZKProtocolGUI(root)
    
    def on_closing():
        if app.protocol_running:
            if messagebox.askokcancel("Выход", "Протокол выполняется. Завершить?"):
                app.protocol_running = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()