import flet as ft

ft.context.disable_auto_update()

def main(page: ft.Page):
    page.title = "P2P App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    status = ft.Text("Pronto", size=16)
    
    def btn1_click(e):
        status.value = "Função 1 executada!"
        # Chame sua função aqui
        page.update()
    
    def btn2_click(e):
        status.value = "Função 2 executada!"
        # Chame sua função aqui
        page.update()
    
    def btn3_click(e):
        status.value = "Função 3 executada!"
        # Chame sua função aqui
        page.update()
    
    page.add(
        ft.Row(
            [
                ft.Button("Botão 1", on_click=btn1_click),
                ft.Button("Botão 2", on_click=btn2_click),
                ft.Button("Botão 3", on_click=btn3_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        ),
        ft.Container(height=20),
        ft.Row([status], alignment=ft.MainAxisAlignment.CENTER),
    )

    page.update()


ft.run(main)
