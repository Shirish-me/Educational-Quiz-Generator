from transformers import pipeline
import random

# Load the question generation pipeline from Hugging Face
question_generator = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")

def generate_mcq(sentence):
    """
    Generate a multiple-choice question based on a given sentence.
    Args:
    - sentence: str, input sentence for question generation

    Returns:
    - mcq: dict, dictionary containing question, options, and answer
    """
    try:
        # Generate a question using the pipeline
        question = question_generator(sentence)
        
        # Extract the correct answer
        correct_answer = question[0]['answer']
        
        # Generate incorrect options (simple heuristic, improve for better results)
        incorrect_answers = [correct_answer[:-1] + chr((ord(correct_answer[-1]) + i) % 122) for i in range(1, 4)]
        
        # Create the question dictionary
        mcq = {
            "question": question[0]['question'],
            "options": [correct_answer] + incorrect_answers,
            "answer": correct_answer
        }
        
        # Shuffle the options to avoid placing the correct answer in the same position
        random.shuffle(mcq['options'])
    except Exception as e:
        print(f"Error generating question: {e}")
        mcq = None
    return mcq
