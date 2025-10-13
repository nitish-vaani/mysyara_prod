import './index.css'

const Tryout = () => {
    return (
        <div className='tryout'>

            <h1>
                Try our  <span>AI phone agents</span> today!</h1>
            <h3><div className="circle"></div> <div className="text">Natural Conversations with human-like voice</div></h3>
            <h3><div className="circle"></div><div className="text">Empathic, Multilingual agents with tone modulation</div></h3>
            <h3><div className="circle"></div><div className="text"> Fully Secure, Compliant & Automated calls</div></h3>
            <h3><div className="circle"></div><div className="text">Can be tailored and hyper-personalized for every user</div></h3>
            <h3><div className="circle"></div><div className="text">Introduce human-in-the-loop for better conversion</div></h3>

            <h2>
                We’re working hard towards optimizing our AI and improving its performance.
                You can help us by providing your valuable&nbsp;
                <span className="feedback-home">
                    <i className="pi pi-comment"></i> {" feedback"}
                </span>
                &nbsp; about your call experience.
            </h2>



        </div>
    );
}

export default Tryout;