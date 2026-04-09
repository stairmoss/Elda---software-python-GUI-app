import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from elda.control.tools import SystemTools, TOOLS_SCHEMA
import json

class LaptopAgent:
    def __init__(self):
        print("Loading Laptop Agent (FunctionGemma-270m)...")
        model_id = "google/functiongemma-270m-it"
        
        # Determine device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Running on {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            if self.device == "cpu":
                self.model.to("cpu")
            print("Laptop Agent Loaded.")
        except Exception as e:
            print(f"Failed to load FunctionGemma: {e}")
            self.model = None

    def execute_command(self, user_query):
        """
        Takes a natural language query (e.g. 'Turn volume up') 
        and executes the corresponding tool.
        """
        if not self.model:
            return "Control Agent not active."
            
        print(f"LaptopAgent Thinking: {user_query}")
        
        # FunctionGemma Prompt Format
        # <start_of_turn>user
        # {content}<end_of_turn>
        # <start_of_turn>model
        
        messages = [
            {"role": "user", "content": user_query}
        ]
        
        # Apply structured tool template
        # The tokenizer.apply_chat_template handles the function definitions for FunctionGemma
        try:
            inputs = self.tokenizer.apply_chat_template(
                messages, 
                tools=TOOLS_SCHEMA, 
                return_tensors="pt", 
                add_generation_prompt=True
            ).to(self.device)
            
            outputs = self.model.generate(inputs, max_new_tokens=128)
            decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the actual model response part (simple parsing logic)
            # FunctionGemma usually outputs specific tags or just the function call string
            # For robustness in this prototype, let's look for known function names
            result_msg = self.parse_and_execute(decoded)
            return result_msg
            
        except Exception as e:
            return f"Agent Error: {e}"

    def parse_and_execute(self, model_output):
        print(f"Model Output: {model_output}")
        # Parse logic. FunctionGemma is fine-tuned to output:
        # <function_call> {"name": "...", "arguments": {...}}
        
        # Simple extraction strategy for prototype
        try:
            start_tag = "<function_call>"
            if start_tag in model_output:
                json_str = model_output.split(start_tag)[1].split("</function_call>")[0].strip()
                call_data = json.loads(json_str)
                func_name = call_data.get("name")
                args = call_data.get("arguments", {})
                
                print(f"Calling Function: {func_name} with {args}")
                
                if func_name == "set_volume":
                    return SystemTools.set_volume(int(args.get("level", 50)))
                elif func_name == "set_brightness":
                    return SystemTools.set_brightness(int(args.get("level", 50)))
                elif func_name == "open_application":
                    return SystemTools.open_application(args.get("app_name", ""))
                else:
                    return "Unknown command function."
            
            # Fallback if no function call found
            return "I couldn't understand how to control the laptop for that."
            
        except Exception as e:
            return f"Parsing Error: {e}"
