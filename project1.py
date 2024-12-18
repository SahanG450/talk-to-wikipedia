import wikipedia as wp  # Wikipedia library
import streamlit as st  # Frontend handling
import pyttsx3  # Speaker handling
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def create_pdf(query, sample, name):
    # Create a BytesIO buffer
    pdf_file = BytesIO()

    # Create a SimpleDocTemplate
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)

    # Get the default style
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    title_style = styles["Title"]

    # Create content for the PDF
    elements = []

    # Add a title
    title = Paragraph("User Information", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))  # Add space after title

    # Add user details
    name_paragraph = Paragraph(f"Name :=> {name}", normal_style)
    query_paragraph = Paragraph(f"Input :=> {query}", normal_style)
    sample_paragraph = Paragraph(f"Information\n {sample}", normal_style)

    # Append to the elements list
    elements.append(name_paragraph)
    elements.append(Spacer(1, 12))
    elements.append(query_paragraph)
    elements.append(Spacer(1, 12))
    elements.append(sample_paragraph)

    # Build the PDF
    doc.build(elements)

    # Move the buffer's cursor to the beginning
    pdf_file.seek(0)
    return pdf_file


# Function to handle text-to-speech
def test_speaker_with_tts(sample, name):
    engine = pyttsx3.init()
    engine.say(f"{sample} Thank you {name}, if you want another some thing, follow the above URL")
    engine.runAndWait()


# Function to handle Wikipedia search
def search_query(query, name):
    if not query.strip():
        st.write("Please enter a valid query to search Wikipedia!")
        return

    try:
        # Perform Wikipedia search
        results = wp.search(query, results=5)
        st.write(f"Search results for '{query}':")

        for i, result in enumerate(results):
            st.write(f"{i + 1}. {result}")

        if results:
            # Fetch the first result and its details
            first_result = results[0]
            page = wp.page(first_result)
            st.write(f"\n**Fetching summary for '{first_result}':**")
            sample = wp.summary(first_result, sentences=4)
            st.write(sample)
            st.write(f"[Read the full article here]({page.url})")

            # Text-to-speech for summary
            test_speaker_with_tts(sample, name)

            # Generate PDF and add download button
            pdf_data = create_pdf(query, sample, name)
            st.download_button(
                label="Download PDF",
                data=pdf_data.getvalue(),
                file_name="user_info.pdf",
                mime="application/pdf",
            )
        else:
            st.write("No results found. Please try a different query.")

    except wp.exceptions.DisambiguationError as e:
        st.write("**Disambiguation error:** The query is too broad. Try one of these options:")
        for option in e.options[:5]:
            st.write(f"- {option}")
    except wp.exceptions.PageError:
        st.write(f"**Error:** The page '{query}' does not exist on Wikipedia.")
    except Exception as e:
        st.write(f"**An unexpected error occurred:** {e}")


# Main function to start the process
def search_start(query, name):
    if st.button("Search"):
        if query and name:
            search_query(query, name)
        else:
            st.write("Please enter both a query and your name!")


# Frontend input handling
name = st.text_input("Enter Your Name: ")  # Get user name
query = st.text_input("Enter your search query:")  # Get query to search on Wikipedia
search_start(query, name)
