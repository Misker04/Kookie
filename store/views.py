from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import Feedback, Product, Promotion, StoreSection, Support
import json
from google.cloud import dialogflow_v2 as dialogflow
from django.http import JsonResponse
import uuid
from django.http import JsonResponse
from google.cloud import dialogflow_v2 as dialogflow
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def dialogflow_query(request):
    if request.method == "POST":
        # Get or generate a session ID
        session_id = request.session.get('dialogflow_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['dialogflow_session_id'] = session_id

        # User input from the request
        user_input = request.POST.get("query", "")

        # Dialogflow setup
        project_id = "mygcpproject-438000"  # Replace with your GCP project ID
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        # Create Dialogflow query
        text_input = dialogflow.TextInput(text=user_input, language_code="en-US")
        query_input = dialogflow.QueryInput(text=text_input)

        # Get response from Dialogflow
        response = session_client.detect_intent(request={"session": session, "query_input": query_input})
        fulfillment_text = response.query_result.fulfillment_text

        # Send response back to the frontend
        return JsonResponse({
            "fulfillment_text": fulfillment_text,
            "intent": response.query_result.intent.display_name,
            "parameters": response.query_result.parameters,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

def index(request):
    return render(request, 'index.html')

def process_command(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        command = data.get('command', '').strip().lower()

        # Check if the user is in feedback mode
        feedback_in_progress = request.session.get('feedback_in_progress', False)

        # Feedback command logic
        if "feedback" in command:
            if feedback_in_progress:
                # If feedback is already in progress, ask for the actual feedback
                response = "Please provide your feedback."
                # Set the session flag to wait for the actual feedback
                request.session['waiting_for_feedback'] = True
            else:
                # Start feedback process, prompt user for actual feedback
                response = "Thank you for your interest in giving feedback! Please provide your feedback after the command."
                request.session['feedback_in_progress'] = True
                request.session['waiting_for_feedback'] = True

        # If feedback was started, but waiting for actual feedback
        elif request.session.get('waiting_for_feedback', False):
            # If the user is providing actual feedback after the "feedback" command
            feedback_message = command.strip()

            if feedback_message:
                # Save the feedback to the database
                new_feedback = Feedback(comments=feedback_message)
                new_feedback.save()

                # Respond with a thank you message
                response = "Thank you for your feedback! We appreciate your input."

                # Reset the session state
                request.session['feedback_in_progress'] = False
                request.session['waiting_for_feedback'] = False
            else:
                # If no feedback provided, prompt again
                response = "You didn't provide any feedback. Please try again."

        # Product search logic (this is simplified)
        elif "find me a" in command:
            try:
                words = command.split(" ")

                # Extract product name, color, and size (with default handling if parts are missing)
                if len(words) < 5:
                    response = "Please provide enough information (e.g., 'find me a black shirt in size small')."
                else:
                    product_name = words[3]  # Extract product description (support multi-word names)
                    color = words[4]  # Extract color (second-to-last word)
                    size = words[-1]  # Extract size (last word)
                    print(product_name, color, size)

                    # Query for products matching name, color, and size
                    products = Product.objects.filter(
                        name__icontains=product_name,
                        color__icontains=color,
                        size__icontains=size
                    )
                    print(products)

                    if products:
                        response = f"Found {products.count()} products matching '{product_name}' with color '{color}' and size '{size}':\n"
                        for product in products:
                            response += f"- {product.name}, {product.color}, {product.size}, ${product.price}\n"
                    else:
                        response = f"No products found matching '{product_name}' with color '{color}' and size '{size}'."
            
            except IndexError:
                response = "Sorry, I couldn't understand the product name, color, or size you are looking for."

        # Promotions logic
        elif "promotions" in command:
            # Fetch active promotions that are currently running
            promotions = Promotion.objects.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )

            if promotions.exists():
                response = "Current promotions: "
                for promo in promotions:
                    response += f"{promo.title} - {promo.discount_percentage}% off\n"
            else:
                response = "No promotions available at the moment."

        # Personalized Recommendations for specific use cases (e.g., trekking shoes)
        elif "suggest" in command and "shoes" in command:
            # Check for use case like "trekking"
            if "trekking" in command:
                footwear = Product.objects.filter(category="footwear", use_case__icontains="trekking")

                if footwear.exists():
                    response = "Here are some shoes recommended for trekking:\n"
                    for item in footwear:
                        response += f"- {item.name}, {item.style}, {item.size}, ${item.price}\n"
                else:
                    response = "Sorry, we don't have any trekking shoes available at the moment."

            elif "running" in command:
                footwear = Product.objects.filter(category="footwear", use_case__icontains="running")

                if footwear.exists():
                    response = "Here are some shoes recommended for running:\n"
                    for item in footwear:
                        response += f"- {item.name}, {item.style}, {item.size}, ${item.price}\n"
                else:
                    response = "Sorry, we don't have any running shoes available at the moment."

        elif "suggest" in command and "clothes" in command:
            # Check for use case like "sports"
            if "sports" in command:
                clothing = Product.objects.filter(category="clothing", use_case__icontains="sports")

                if clothing.exists():
                    response = "Here are some clothes recommended for sports:\n"
                    for item in clothing:
                        response += f"- {item.name}, {item.material}, {item.size}, ${item.price}\n"
                else:
                    response = "Sorry, we don't have any sports clothing available at the moment."

            elif "formal" in command:
                clothing = Product.objects.filter(category="clothing", use_case__icontains="formal")

                if clothing.exists():
                    response = "Here are some formal clothing options:\n"
                    for item in clothing:
                        response += f"- {item.name}, {item.material}, {item.size}, ${item.price}\n"
                else:
                    response = "Sorry, we don't have any formal clothing available at the moment."
        
        # Navigation to store sections (new feature)
        elif "take me to the" in command:
            section_name = command.replace("take me to the", "").strip()  # Extract section name
            try:
                # Query the store sections for the provided name (case-insensitive)
                section = StoreSection.objects.filter(name__icontains=section_name).first()

                if section:
                    response = f"Sure! The {section_name} section is located at {section.location}. {section.description}"
                else:
                    response = f"Sorry, I couldn't find the {section_name} section. Please check the section name and try again."
            except Exception as e:
                response = f"Error while processing your request: {str(e)}"

        # Handle Customer Support Inquiries (e.g., return policy)
        elif "return" in command or "refund" in command:
            # You can fetch the support information from the database or hardcode the response
            try:
                # Fetching the support information (e.g., return policy)
                if "return" in command:
                    support_query = Support.objects.filter(query__icontains="return").first()
                elif "refund" in command:
                    support_query = Support.objects.filter(query__icontains="refund").first()

                if support_query:
                    response = support_query.response

            except Support.DoesNotExist:
                response = "Sorry, unable to process your request. Please try again or talk to any staff member."

        # If command doesn't match any known functionality
        else:
            response = "Sorry, I didn't understand that command."

        return JsonResponse({'response': response})

    return JsonResponse({'response': 'Invalid request'}, status=400)

