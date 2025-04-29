# library(dotenv)
# library(shiny)
# library(shinychat)
# library(ellmer)
# library(bslib)
#
# prompt <- paste(readLines("prompt.generated.md"), collapse = "\n")
#
# ui <- page_fluid(
#   class = "pt-5",
#   tags$style("a:not(:hover) { text-decoration: none; }"),
#   chat_ui("chat")
# )
#
# server <- function(input, output, session) {
#   chat <- chat_openai(model = "gpt-4o", system_prompt = prompt)
#   # chat <- chat_claude(model = "claude-3-5-sonnet-latest", system_prompt = prompt)
#   observeEvent(input$chat_user_input, {
#     chat_append("chat", chat$stream_async(input$chat_user_input))
#   })
#   chat_append("chat", "👋 Hi, I'm **Ellmer Assistant**! I'm here to answer questions about [ellmer](https://github.com/tidyverse/ellmer) and [shinychat](https://github.com/posit-dev/shinychat), or to generate code for you.")
# }
#
# shinyApp(ui, server)

from pathlib import Path

import dotenv
from chatlas import ChatOpenAI
from shiny import App, reactive, ui

dotenv.load_dotenv()

with open(Path(__file__).parent / "prompt.generated.md") as f:
    system_prompt = f.read()


def app_ui(request):
    return ui.page_fluid(
        ui.tags.style("a:not(:hover) { text-decoration: none; }"),
        ui.tags.style("#clear { display: none; }", id="hide_new_convo_css"),
        ui.tags.a(
            "📄 New Chat",
            href="./",
            id="clear",
            class_="btn btn-sm btn-default float-right bg-light shadow",
            style="position: fixed; top: 0.5rem; left: 50%; transform: translateX(-50%);",
        ),
        ui.chat_ui(
            "chat",
            messages=[
                "👋 Hi, I'm **Ellmer Assistant**! I'm here to answer questions about [ellmer](https://github.com/tidyverse/ellmer) and [shinychat](https://github.com/posit-dev/shinychat), or to generate code for you."
            ],
        ),
        class_="pt-5",
    )


def server(input, output, session):
    chat_client = ChatOpenAI(system_prompt=system_prompt, model="gpt-4.1")
    chat = ui.Chat("chat")
    chat.enable_bookmarking(chat_client, bookmark_on="response")

    @chat.on_user_submit
    async def chat_on_user_submit(user_input):
        resp = await chat_client.stream_async(user_input)
        await chat.append_message_stream(resp)
    
    @reactive.effect
    def bookmark_on_restore():
        if len(chat.messages()) > 1:
            ui.remove_ui("#hide_new_convo_css")
            bookmark_on_restore.destroy()


app = App(app_ui, server, bookmark_store="url")
