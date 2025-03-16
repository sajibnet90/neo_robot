from app.services.query_generators.query_service import QueryService
from app.services.ai_service import AIService
from app.core.error_codes import ErrorCode
from app.utils.json_utils import clean_and_parse_json

class ResponseService:
    """
    Handles AI-based processing of user queries.
    """

    @staticmethod
    def handle_request(cleaned_input: str, query_id: str, reference_query_id: str = None) -> dict:
        """
        Processes a cleaned user input by:
        1. Generating an AI extraction query.
        2. Calling AI to get structured JSON output.
        3. Formatting the final AI query.
        4. Calling AI to generate the final response.
        """

        ai_extraction_query = QueryService.query_request(cleaned_input)

        # Call AIService to get a raw string response
        ai_raw_response = AIService.call_ai_model(ai_extraction_query)

        # Clean and parse JSON externally
        extracted_json = clean_and_parse_json(ai_raw_response)

        if "error" in extracted_json:
            return {
                "queryId": query_id,
                "error": "AI failed to extract query details.",
                "error_code": ErrorCode.AI_PROCESSING_ERROR.value
            }

        # Attach queryId and referenceQueryId to extracted JSON
        extracted_json["queryId"] = query_id
        extracted_json["followUp"]["referenceQueryId"] = reference_query_id

        # Generate the final AI query using structured JSON
        ai_query = QueryService.generate_final_query(extracted_json)

        # Call AI Model again to get final response
        ai_response = AIService.call_ai_model(ai_query)

        # Handle AI failure in response generation
        if "error" in ai_response:
            return {
                "queryId": query_id,
                "error": ai_response,
                "error_code": ErrorCode.AI_PROCESSING_ERROR.value
            }

        return {
            "queryId": query_id,
            "response": ai_response,
            "source": "AI",
            "cached": False,
            "followUp": {
                "status": extracted_json["followUp"]["status"],
                "referenceQueryId": reference_query_id
            }
        }