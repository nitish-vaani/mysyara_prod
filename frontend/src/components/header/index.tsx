// import { useNavigate } from "react-router-dom";
// import sbi from "../../assets/logos/sbi.png"
// import avatar from "../../assets/logos/user_gray.png"
// import { Menubar } from "primereact/menubar";
// import { Badge } from "primereact/badge";
// import { pagePaths } from "../../common/constants";

// const Header = () => {

//   const navigate = useNavigate();
//   const name = localStorage.getItem("Name");


//   const itemRenderer = (item: any) => (
//     <a className="p-menuitem-link" onClick={handleLogout}>
//       <span className={item.icon} />
//       <span className="mx-2">{item.label}</span>
//       {item.badge && <Badge className="ml-auto" value={item.badge} />}
//       {item.shortcut && <span className="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">{item.shortcut}</span>}
//     </a>
//   );

//   const items = [
//     {
//       label: name || "Guest",
//       items: [{
//         label: 'Sign out',
//         template: itemRenderer
//       }
//       ]
//     }
//   ];

//   const menuItems = [
//     {
//       label: "Call Test",
//       icon: "pi pi-phone",
//       url:pagePaths.home

//     }
//     ,
//     {
//       label: "Call History",
//       icon: "pi pi-history",
//       url:pagePaths.history
//     }
//     ,
//     {
//       label: "Feedback",
//       icon: "pi pi-comment",
//       url:pagePaths.feedback

//     }
//   ];

//   const handleLogout = () => {
//     localStorage.clear();
//     navigate(pagePaths.signin);
//   };

//   const start = <img className="avatar-user" src={avatar} alt="" />

//   return (
//     <div className="home">
//       <section className="header">
//       <img className="sbi-home" src={sbi} />
//         <div className="menu">
//           <Menubar model={menuItems} />
//         </div>
//         <div className="avatar">
//           <div className="card">
//             <Menubar start={start} model={items} />
//           </div>
//         </div>
//       </section>
//       </div>
//   );
// };

// export default Header;


import { useNavigate } from "react-router-dom";
import sbi from "../../assets/logos/sbi.png"
import avatar from "../../assets/logos/user_gray.png"
import { Menubar } from "primereact/menubar";
import { Badge } from "primereact/badge";
import { pagePaths } from "../../common/constants";

const Header = () => {

  const navigate = useNavigate();
  const name = localStorage.getItem("Name");


  const itemRenderer = (item: any) => (
    <a className="p-menuitem-link" onClick={handleLogout}>
      <span className={item.icon} />
      <span className="mx-2">{item.label}</span>
      {item.badge && <Badge className="ml-auto" value={item.badge} />}
      {item.shortcut && <span className="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">{item.shortcut}</span>}
    </a>
  );

  const items = [
    {
      label: name || "Guest",
      items: [{
        label: 'Sign out',
        template: itemRenderer
      }
      ]
    }
  ];

  const menuItems = [
    {
      label: "Dashboard",
      icon: "pi pi-chart-bar",
      url: pagePaths.dashboard
    },
    {
      label: "Call Test",
      icon: "pi pi-phone",
      url: pagePaths.home
    },
    {
      label: "Call History",
      icon: "pi pi-history",
      url: pagePaths.history
    },
    {
      label: "Feedback",
      icon: "pi pi-comment",
      url: pagePaths.feedback
    }
  ];

  const handleLogout = () => {
    localStorage.clear();
    navigate(pagePaths.signin);
  };

  const start = <img className="avatar-user" src={avatar} alt="" />

  return (
    <div className="home">
      <section className="header">
      <img className="sbi-home" src={sbi} />
        <div className="menu">
          <Menubar model={menuItems} />
        </div>
        <div className="avatar">
          <div className="card">
            <Menubar start={start} model={items} />
          </div>
        </div>
      </section>
      </div>
  );
};

export default Header;