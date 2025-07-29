"""Integration tests for the FastAPI application."""


class TestAPI:
    """Test cases for the FastAPI application."""

    def test_review_endpoint_valid_request(self, test_client):
        """Test review endpoint with valid request."""
        request_data = {
            "product_name": "Educational Course",
            "sales_page": "Evidence-based strategies backed by psychology research for better learning outcomes."
        }

        response = test_client.post("/review", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "decision" in data
        assert data["decision"] in ["approve", "reject"]
        assert "explanation" in data
        assert len(data["explanation"]) >= 10

    def test_review_endpoint_samples(self, test_client):
        """Test review endpoint with the provided sample data."""
        # Sample data from the challenge
        samples = [
            {
                "product_name": "Keto Mastery E-Book",
                "sales_page": "Lose 15kg in 21 days! 100% guaranteed…",
                "expected_decision": "reject"
            },
            {
                "product_name": "Crypto Signals 999",
                "sales_page": "Our bot turns €100 into €10,000 overnight with no risk!",
                "expected_decision": "reject"
            },
            {
                "product_name": "Mindful Productivity Course",
                "sales_page": "Evidence-based strategies backed by psychology and behavioral science.",
                "expected_decision": "approve"
            },
            {
                "product_name": "Medicinal Garden Kit",
                "sales_page": "A Complete Natural Pharmacy in Your Backyard I made this Medicinal Garden Kit because I wanted to empower other people to take their health into their own hands. I think everyone should have a medicinal garden in their backyard. This way you can easily go and pick the remedy you need at any time. Your backyard pharmacy will be there for you even in times of crisis when pharmacies might be closed or looted.   Imagine stepping into your backyard and looking at your new colorful medicinal garden. Your backyard will smell of fresh lavender and chamomile.  You can pick any of these medicinal plants and turn it into the remedy you need. I’ve gathered all the seeds for 10 herbs, inside the Medicinal Garden Kit. All these seeds have been handpicked from the very best plants, as I wanted nothing less than premium quality seeds.  With your seeds kit, you’ll also receive a FREE copy of Herbal Medicinal Guide: From Seeds to Remedies. This guide will show you how to turn these 10 plants into tinctures, ointments, salves, poultices, decoctions, infusions, essential oils —all in minute detail so you can follow our guide even if you’ve never made an herbal medicine in your life.",
                "expected_decision": "approve"
            },
                        {
                "product_name": "Home Doctor Book",
                "sales_page": "The Home Doctor - Practical Medicine for Every Household - is a 304 page doctor written and approved guide on how to manage most health situations when help is not on the way. If you want to see what happens when things go south, all you have to do is look at Venezuela: no electricity, no running water, no law, no antibiotics, no painkillers, no anesthetics, no insulin or other important things. But if you want to find out how you can still manage in a situation like this, you must also look to Venezuela and learn the ingenious ways they developed to cope.",
                "expected_decision": "approve"
            },
        ]

        for sample in samples:
            request_data = {
                "product_name": sample["product_name"],
                "sales_page": sample["sales_page"]
            }

            response = test_client.post("/review", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["decision"] == sample["expected_decision"], \
                f"Expected {sample['expected_decision']} for {sample['product_name']}, got {data['decision']}"

    def test_review_endpoint_empty_input(self, test_client):
        """Test review endpoint with empty input."""
        request_data = {
            "product_name": "",
            "sales_page": ""
        }

        response = test_client.post("/review", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_review_endpoint_missing_fields(self, test_client):
        """Test review endpoint with missing required fields."""
        # Missing product_name
        response = test_client.post("/review", json={"sales_page": "Some content"})
        assert response.status_code == 422

        # Missing sales_page
        response = test_client.post("/review", json={"product_name": "Some name"})
        assert response.status_code == 422
