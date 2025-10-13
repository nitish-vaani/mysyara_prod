import { Slider } from "primereact/slider";
import './index.css'
import { useRef, useState } from 'react';
import Icon from '../../assets/logos/feedback_black.png'
import { FeedbackRequest } from "../../common/types";
import { Toast } from "primereact/toast";
import { submitFeedback } from "../../common/api";

const Feedback = () => {

    const [feedback,setFeedback] =  useState<FeedbackRequest>({conversation_id:"",
        feedback_text:"",
        felt_natural:5,
        interruptions:5,
        response_speed:5,
        user_id:localStorage.getItem("fullName")||""
    });

    const ratingScale = [
        "Really Bad",
        "Terrible",
        "Poor",
        "Below Average",
        "Mediocre",
        "Acceptable",
        "Decent",
        "Good",
        "Very Good",
        "Great"
    ];

    const responseSpeed = [
        "Slow response",
        "Laggy",
        "Sluggish",
        "Somewhat delayed",
        "Moderate speed",
        "Reasonable response time",
        "Fairly fast",
        "Fast",
        "Near optimal",
        "Optimal"
    ];

    const handleNaturalSlide = (e: any) => {
        console.log(e.value);
        setFeedback((p)=>({...p,felt_natural:e.value}) );
    }

    const handleDelaySlide = (e: any) => {
        console.log(e.value);
        setFeedback((p)=>({...p,response_speed:e.value}) );
    }

    const handleTurnSlide = (e: any) => {
        console.log(e.value);
        setFeedback((p)=>({...p,interruptions:e.value}) );
    }

    const onclick = async () =>{
       
         await submitFeedback(feedback);
        show("Thank you for your feedback")

    }

        const toast = useRef<Toast>(null);
        const show = (summary:string) => {
        toast.current?.show({severity:'success', summary, life: 3000});
    };
    return (
        <>
        <Toast ref={toast} position="bottom-right" />
        <div className='feedback'>
      

            <div className='feedback-body'>

                <div className='feedback-text'>
                    <h1 className='improve-vaani'>
                        <img src={Icon} alt="" />
                        Help us improve Vaani
                    </h1>
                    <textarea
                    value={feedback.feedback_text}
                    onChange={(e)=>setFeedback((prevFeedback) => ({
                        ...prevFeedback,
                        feedback_text: e.target.value,
                    }))}
                        rows={15}
                        cols={60}
                        placeholder='Tell us about your call experience and any specific things which you think we should work on...'>
                    </textarea>
                </div>
                <span className='feedback-form'>

                    <p>Felt Natural?: <span className="small-gray">{ratingScale[feedback.felt_natural]}</span></p>
                    <div>
                        <span>Not at all</span>
                        <Slider value={feedback.felt_natural} onChange={handleNaturalSlide} className="w-14rem" step={1} max={9} min={0} />
                        <span>Great</span>
                    </div>

                    <p>Delays: <span className="small-gray">{responseSpeed[feedback.response_speed]}</span></p>
                    <div>
                        <span>Slow response</span>
                        <Slider value={feedback.response_speed} onChange={handleDelaySlide} className="w-14rem" step={1} max={9} min={0} />
                        <span>Optimal</span>
                    </div>

                    <p>Interruptions & Turn-taking: <span className="small-gray">{ratingScale[feedback.interruptions]}</span></p>
                    <div>
                        <span>Not at all</span>
                        <Slider value={feedback.interruptions} onChange={handleTurnSlide} className="w-14rem" step={1} max={9} min={0} />
                        <span>Great</span>
                    </div>

                </span>
            </div>
            <button  onClick={onclick} >
                SUBMIT
            </button>

        </div>
        </>

    );

}

export default Feedback;