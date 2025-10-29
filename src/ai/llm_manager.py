"""
Insyte AI - LLM Manager
Lightweight wrapper around a Hugging Face transformers causal LM.

This manager provides a minimal, offline-capable API used by the
Streamlit dashboard: lazy model loading, status reporting, and a
generate_response() helper. It defaults to a small model (gpt2) to
avoid large downloads during development but can be configured.

The implementation is intentionally simple so the dashboard can run
without heavy model requirements. In production you can swap this
for a more advanced manager that supports device placement, quantized
models, or adapter layers.
"""

from typing import Dict, Any, Optional
import logging

try:
	from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
	import torch
except Exception:
	# If transformers or torch are not available at runtime, we still
	# provide a fallback stub implementation so imports don't fail.
	AutoModelForCausalLM = None
	AutoTokenizer = None
	pipeline = None
	torch = None


class LLMManager:
	"""Minimal LLM manager used by the Streamlit dashboard.

	Methods expected by the dashboard:
	  - get_model_info() -> Dict[str, Any]
	  - load_model() -> bool
	  - generate_response(prompt: str) -> str
	"""

	# System prompt to guide the model as a productivity assistant
	SYSTEM_PROMPT = """You are Insyte AI, a helpful productivity assistant and personal mentor. Your role is to:
- Provide practical, actionable advice on productivity, time management, and work-life balance
- Guide users with clear, structured responses
- Give specific tips and techniques that can be immediately applied
- Be encouraging and supportive while being professional
- Keep responses focused and concise (3-5 key points)
- Use examples when helpful

Always be helpful, accurate, and mentor-like in your guidance."""

	def __init__(self, model_name: str = "gpt2"):
		self.model_name = model_name
		self.model = None
		self.tokenizer = None
		self.generator = None
		self.device = "cpu"
		self.logger = logging.getLogger(__name__)

	def get_model_info(self) -> Dict[str, Any]:
		"""Return basic status about the LLM."""
		if self.model is None and self.generator is None:
			return {"status": "not_loaded"}

		return {
			"status": "loaded",
			"model_name": self.model_name,
			"device": self.device,
		}

	def load_model(self) -> bool:
		"""Load the tokenizer/model (lazy). Returns True on success.

		This uses a small default model (gpt2) to keep resource usage low.
		If transformers/torch are not installed, this returns False.
		"""
		if pipeline is None:
			self.logger.error("transformers or torch not available; cannot load model")
			return False

		try:
			# Pick device
			if torch is not None and torch.cuda.is_available():
				self.device = "cuda"
			else:
				self.device = "cpu"

			# Use transformers pipeline for text-generation for simplicity
			self.generator = pipeline(
				"text-generation",
				model=self.model_name,
				device=0 if self.device == "cuda" else -1,
			)

			# Keep references for potential advanced usage
			self.model = None
			self.tokenizer = None

			self.logger.info(f"Loaded LLM model: {self.model_name} on {self.device}")
			return True

		except Exception as e:
			self.logger.error(f"Failed to load LLM model: {e}")
			return False

	def generate_response(self, prompt: str, max_length: int = 200) -> str:
		"""Generate a response as a productivity assistant.

		Raises RuntimeError if the model is not loaded.
		"""
		if self.generator is None:
			raise RuntimeError("LLM model not loaded. Call load_model() first.")

		# Format prompt with system context for better responses
		formatted_prompt = f"""As a productivity assistant, help with this question:

Question: {prompt}

Answer:"""

		try:
			outputs = self.generator(
				formatted_prompt, 
				max_length=max_length,
				do_sample=True,
				top_p=0.92,
				top_k=50,
				temperature=0.8,
				num_return_sequences=1,
				pad_token_id=self.generator.tokenizer.eos_token_id,
				repetition_penalty=1.2,
				no_repeat_ngram_size=3
			)
			
			if isinstance(outputs, list) and outputs:
				text = outputs[0].get("generated_text", "")
				
				# Extract only the answer part
				if "Answer:" in text:
					answer = text.split("Answer:")[-1].strip()
					# Clean up the response
					answer = answer.split("\n\n")[0]  # Take first paragraph
					if answer:
						return answer
				
				# Fallback: return generated text after prompt
				if text.startswith(formatted_prompt):
					return text[len(formatted_prompt):].strip()
				
				return text.strip() if text else "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."

			return "I apologize, but I couldn't generate a response. Please try again."

		except Exception as e:
			self.logger.error(f"Error during generation: {e}")
			return f"I encountered an error while generating a response. Please try again or check the model settings."


class LLMStub(LLMManager):
	"""Fallback lightweight stub used when transformers are unavailable.

	It provides deterministic canned responses so the dashboard remains usable
	in environments without heavy ML dependencies.
	"""

	def load_model(self) -> bool:
		self.device = "none"
		self.generator = lambda prompt, max_length=128, **k: [{"generated_text": prompt + "\n(LLM stub response)"}]
		return True

	def generate_response(self, prompt: str, max_length: int = 128) -> str:
		if self.generator is None:
			raise RuntimeError("LLM stub not initialized")
		outputs = self.generator(prompt, max_length=max_length)
		return outputs[0].get("generated_text", "").replace(prompt, "").strip()


# If transformers aren't present, exports still provide a usable class name
if pipeline is None:
	# Export LLMManager name pointing to the stub so imports succeed
	LLMManager = LLMStub
