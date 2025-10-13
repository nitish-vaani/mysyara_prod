import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./index.css"
import { InputText } from "primereact/inputtext";
import { Password } from "primereact/password";
import { Button } from "primereact/button";
import { FloatLabel } from "primereact/floatlabel";
import { Toast } from 'primereact/toast';
import { loginUser } from "../../common/api";

const SignInForm = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState<boolean>(false);
    const navigate = useNavigate();

    const handleLogin = async () => {
        setLoading(true);
        try{
            const user = await loginUser({username,password});
            if (user.status <= 299) {
                localStorage.setItem("isAuth", "true");
                localStorage.setItem("fullName", user.data.user_id);
                localStorage.setItem("Name", user.data.user_name);
                navigate("/home");
            } else {
               show("Invalid Credentails");
            }
        } catch(error) {
            show("Something went wrong");
        }
      setLoading(false);
    };

    const toast = useRef<Toast>(null);

    const show = (summary:string) => {
        toast.current?.show({severity:'error', summary, life: 3000});
    };

    return (
        <div className="sign-in-form">
            <Toast ref={toast} position="bottom-right"/>
            <div className="welcome-text">
                <h1>Welcome to Vaani</h1>
                <h3>Enter your credentials to explore how voice AI</h3>
                <h3>  can supercharge your operations.</h3>
            </div>
            <div className="signin-input">
                <div>
                    <FloatLabel>
                        <label htmlFor="username" > Enter your user name</label>
                        <InputText style={{ width: '100%' }} className="w-full" id="username" variant="filled" value={username} onChange={(e) => setUsername(e.target.value)} disabled={loading} />
                    </FloatLabel>
                </div>
                <div>
                    <FloatLabel>
                        <Password style={{ width: '100%' }} className="w-full" inputId="passwordtext"
                            pt={{ input: { className: 'w-full' } }} variant="filled" value={password} onChange={(e) => setPassword(e.target.value)} feedback={false} tabIndex={1} toggleMask disabled={loading}/>
                             <label htmlFor="passwordtext">Enter your password</label>
                    </FloatLabel>
                </div>
                <Button className="sign-in-button" label="Sign In" onClick={handleLogin} severity="secondary" raised rounded loading={loading}/>
            </div>



        </div>
    );
};

export default SignInForm;
