import flet as ft
import requests
import threading

def main(page: ft.Page):
    page.title = "Domain Status Checker"
    
    # Update window dimensions using the new properties
    page.window.width = 310
    page.window.height = 500

    # UI elements
    file_path_input = ft.TextField(label="File selected:", width=400, disabled=True)
    status_200_counter = ft.Text("200: 0", color="green")
    status_403_counter = ft.Text("403: 0", color="blue")
    status_500_counter = ft.Text("500: 0", color="orange")
    status_other_counter = ft.Text("Other: 0", color="red")
    output_text = ft.Text("")  # Adjust text style if needed

    # Counter variables
    count_200 = count_403 = count_500 = count_other = 0

    # File picker dialog
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_path_input.value = e.files[0].path
            output_text.value = f"Results will be saved to: {e.files[0].path.replace('.txt', '_results.txt')}"
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def check_domains(domains, output_file):
        nonlocal count_200, count_403, count_500, count_other
        count_200 = count_403 = count_500 = count_other = 0

        with open(output_file, 'w') as out_file:
            for domain in domains:
                domain = domain.strip()  # Remove leading/trailing whitespace
                if not domain.startswith('http://') and not domain.startswith('https://'):
                    domain = 'http://' + domain  # Prepend 'http://' if not present
                try:
                    response = requests.get(domain)
                    status = response.status_code
                    if status == 200:
                        count_200 += 1
                        status_text = "working"
                        out_file.write(f"{domain} --- {status_text} --- {status}\n")
                    elif status == 403:
                        count_403 += 1
                        status_text = "forbidden"
                    elif status == 500:
                        count_500 += 1
                        status_text = "server error"
                    else:
                        count_other += 1
                        status_text = "not working"
                    output_text.value += f"{domain} --- {status_text} --- {status}\n"
                    
                except requests.exceptions.RequestException:
                    count_other += 1
                    output_text.value += f"{domain} --- fail to connect\n"

                # Update counters and UI
                page.add(
                    status_200_counter,
                    status_403_counter,
                    status_500_counter,
                    status_other_counter,
                    output_text
                )
                status_200_counter.value = f"200: {count_200}"
                status_403_counter.value = f"403: {count_403}"
                status_500_counter.value = f"500: {count_500}"
                status_other_counter.value = f"Other: {count_other}"
                page.update()

        # Final update of counters after scan is complete
        output_text.value += f"\nDomains with status code 200 saved to: {output_file}"
        page.update()

    def start_checking(e):
        file_path = file_path_input.value
        output_file = file_path.replace('.txt', '_results.txt')

        def run_check():
            try:
                with open(file_path, 'r') as file:
                    domains = file.readlines()
                    output_text.value = ""
                    check_domains(domains, output_file)
            except FileNotFoundError:
                output_text.value = "File not found!"
                page.update()
            except Exception as ex:
                output_text.value = f"An error occurred: {ex}"
                page.update()

        threading.Thread(target=run_check).start()

    # File browse button
    browse_button = ft.ElevatedButton(text="Browse File", on_click=lambda _: file_picker.pick_files(allow_multiple=False))

    # Start button
    start_button = ft.ElevatedButton(text="Start Checking", on_click=start_checking)

    # Layout with buttons next to each other
    page.add(
        file_path_input,
        ft.Row(
            controls=[
                browse_button,
                start_button
            ]
        ),
        status_200_counter,
        status_403_counter,
        status_500_counter,
        status_other_counter,
        output_text
    )

ft.app(target=main)
