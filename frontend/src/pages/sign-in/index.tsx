import { useEffect, useRef } from "react";
import backdrop from "../../assets/videos/backdrop.mp4"
import Form from "../../components/sign-in-form"
import sbi from "../../assets/logos/sbi.png"
import "./index.css"

const SignIn = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
    
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = 0.5;
    }
  }, []);

  return (
    <div className="container">
      <section className="left-section">
        <div>
          <ul className="no-bullets over-backdrop">
            <li><h1>AI That</h1></li>
            <li><h1>Speaks Volumes</h1></li>
            <li><h3>Reinventing everyday conversations,</h3></li>
            <li><h3>One voice at a time</h3></li>
          </ul>
          <video
            src={backdrop}
            ref={videoRef}
            autoPlay
            loop
            muted
            playsInline
            className="backdrop"
          />
        </div>
      </section>
      <section className="right-section">
        <img className="sbi" src={sbi} alt="" />
        <Form />
      </section>
    </div>
  );
};

export default SignIn;
