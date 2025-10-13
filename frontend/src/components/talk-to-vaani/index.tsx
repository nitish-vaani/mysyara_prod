import { Card } from "primereact/card"
import "./index.css"
import { IconField } from "primereact/iconfield";
import { InputIcon } from "primereact/inputicon";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";
import { Dropdown } from "primereact/dropdown";
import { useEffect, useRef, useState } from "react";
import { getAllModels, triggerCall } from "../../common/api";
import { TriggerCallRequest } from "../../common/types";
import { Toast } from "primereact/toast";
import { useNavigate } from "react-router-dom";
import { pagePaths } from "../../common/constants";

type model = {
    model_id: string,
    model_name: string,
}

type CountryCode = {
    code: string,
    label: string,
}

const TalkToVaani = () => {
    const navigate = useNavigate();
    const toast = useRef<Toast>(null);

    const show = (summary: string) => {
        toast.current?.show({ severity: 'info', summary, life: 3000 });
    };

    const [loading, setLoading] = useState<boolean>(false);
    const [formData, setFormData] = useState<any>({});
    const [plans, setPlans] = useState<model[]>([]);
    const [selectedPlan, setSelectedPlan] = useState<model | null>(null);
    const [selectedCountryCode, setSelectedCountryCode] = useState<CountryCode>({ code: "+91", label: "+91" });

    // List of common country codes (simplified)
    const countryCodes: CountryCode[] = [
        { code: "+1", label: "+1" },
        { code: "+44", label: "+44" },
        { code: "+91", label: "+91" },
        { code: "+61", label: "+61" },
        { code: "+86", label: "+86" },
        { code: "+33", label: "+33" },
        { code: "+49", label: "+49" },
        { code: "+81", label: "+81" },
        { code: "+7", label: "+7" },
        { code: "+27", label: "+27" },
        { code: "+971", label: "+971" },
        { code: "+65", label: "+65" },
        { code: "+60", label: "+60" },
        { code: "+34", label: "+34" },
        { code: "+39", label: "+39" },
        { code: "+55", label: "+55" },
        { code: "+82", label: "+82" },
        { code: "+66", label: "+66" },
        { code: "+63", label: "+63" },
        { code: "+64", label: "+64" },
        { code: "+351", label: "+351" },
        { code: "+48", label: "+48" },
        { code: "+420", label: "+420" },
        { code: "+30", label: "+30" },
        { code: "+351", label: "+351" }
    ];

    useEffect(() => {
        getAllModels()
            .then((data: any) => {
                setPlans(data.data);
            })
            .catch((error) => {
                console.error("Error fetching models:", error);
            });
    }, [])

    const talkToVaani = async () => {
        setLoading(true);
        if (selectedPlan && selectedPlan.model_id && formData && formData.contact_number && formData.name) {
            const user = localStorage.getItem('fullName')
            if (user) {
                const req: TriggerCallRequest = {
                    agent_id: selectedPlan.model_id,
                    contact_number: selectedCountryCode.code + formData.contact_number,
                    name: formData.name,
                    user_id: user,
                }

                try {
                    const res = await triggerCall(req);
                    if (res.status <= 299) {
                        // Clear form data and reset selected plan
                        setFormData({});
                        setSelectedPlan(null);
                        show("You will be called by our agent shortly.")
                    } else {
                        show("Something went wrong");
                    }
                } catch (error) {
                    console.error("Error triggering call:", error);
                    show("Error triggering call. Please try again.");
                }
            } else {
                show("Please login first");
                navigate(pagePaths.signin);
            }
        } else {
            show("Please fill all required fields");
        }
        setLoading(false);
    }

    return (
        <Card className="talk-to-vaani">
            <Toast ref={toast} position="bottom-right" />
            <h1>Talk to Vaani 1.0</h1>
            <div>
                <IconField iconPosition="right">
                    <InputIcon className="pi pi-user"> </InputIcon>
                    <InputText 
                        placeholder="your good name?" 
                        value={formData.name || ""} 
                        onChange={(e) => (setFormData({ ...formData, name: e.target.value }))}
                        disabled={loading}
                    />
                </IconField>
                <hr />
            </div>
            <div className="phone-input-container">
                <div className="country-code-dropdown">
                    <Dropdown
                        value={selectedCountryCode}
                        options={countryCodes}
                        onChange={(e) => setSelectedCountryCode(e.value)}
                        optionLabel="label"
                        placeholder="+91"
                        disabled={loading}
                    />
                </div>
                <div className="phone-number-input">
                    <IconField iconPosition="right">
                        <InputIcon className="pi pi-phone"> </InputIcon>
                        <InputText 
                            placeholder="Enter phone number" 
                            value={formData.contact_number || ""} 
                            onChange={(e) => (setFormData({ ...formData, contact_number: e.target.value }))} 
                            keyfilter="int"
                            disabled={loading}
                        />
                    </IconField>
                </div>
                <hr />
            </div>

            <h3>USE-CASE:</h3>
            <div>
                <Dropdown 
                    value={selectedPlan} 
                    onChange={(e) => setSelectedPlan(e.value)} 
                    options={plans} 
                    optionLabel="model_name"
                    placeholder="Select a Plan" 
                    className="w-full md:w-14rem" 
                    disabled={loading}
                />
                <hr />
            </div>

            <Button 
                label="TRIGGER TEST CALL" 
                icon="pi pi-phone" 
                severity="secondary" 
                onClick={talkToVaani} 
                disabled={(!selectedPlan || !formData.contact_number || !formData.name) || loading}
                loading={loading}
            />
        </Card>
    );
};

export default TalkToVaani;