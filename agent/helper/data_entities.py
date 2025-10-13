from dataclasses import dataclass, field
from typing import Optional
from livekit.agents import JobContext, BackgroundAudioPlayer

@dataclass
class UserData:
    "Class to store user and service data during the call"
    ctx: Optional[JobContext] = None

    # customer information
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    car_model: Optional[str] = None
    car_make_year: Optional[str] = None
    approximate_run: Optional[str] = None
    emirate: Optional[str] = None
    location: Optional[str] = None
    service_requested: Optional[str] = None
    bg_audio: Optional[BackgroundAudioPlayer] = None

    def is_identified(self) -> bool:
        """Check if the customer is identified."""
        return self.full_name is not None
    
    def summarize(self) -> str:
        """Return a summary of the customer information."""
        return f"""Customer Information Summary:            
            Full Name: {self.full_name or "Not Provided"}
            Mobile Number: {self.mobile_number or "Not Provided"}
            Car Model: {self.car_model or "Not Provided"}
            Car Make Year: {self.car_make_year or "Not Provided"}
            Approximate Run: {self.approximate_run or "Not Provided"}
            Emirate: {self.emirate or "Not Provided"}
            Location: {self.location or "Not Provided"}
            Service Requested: {self.service_requested or "Not Provided"}"""

