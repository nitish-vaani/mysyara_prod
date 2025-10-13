import { FaHeart } from 'react-icons/fa';
import logo from '../../assets/logos/v.png'

const Footer = () => {
  return (
    <div className="home">
      <section className="footer">
        <div className="vaani-research">
          <h2> <span><img src={logo} alt="" /> </span> <span className="vaani">{"Vaani "}</span><span className="research">Research</span></h2>
        </div>
        <div className="made-in-india">
          <h2>Crafted with <span><FaHeart /></span> in India</h2>
        </div>
      </section>
      </div>
  );
};

export default Footer;
