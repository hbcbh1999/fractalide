#[macro_use]
extern crate rustfbp;
extern crate capnp;

use std::str::FromStr;

agent! {
    print_file_with_feedback, edges(value_string, list_triple)
    inputs(input: list_triple),
    inputs_array(),
    outputs(next: value_string),
    outputs_array(),
    option(),
    acc(),
    fn run(&mut self) -> Result<()> {
        loop{
            let mut ip = try!(self.ports.recv("input"));
            let list_triple: list_triple::Reader = try!(ip.read_schema());
            let list_triple = try!(list_triple.get_triples());
            if try!(list_triple.get(0).get_first()) == "end" {
                println!("{}",try!(list_triple.get(0).get_first()));
                break;
            } else {
                for i in 0..list_triple.len() {
                    let count = try!(list_triple.get(i).get_third());
                    if i32::from_str(count).unwrap() > 1 {
                        println!("{}",try!(list_triple.get(i).get_first()));
                        println!("{}",try!(list_triple.get(i).get_second()));
                        println!("{}",try!(list_triple.get(i).get_third()));
                    }
                }
            }
            let mut next_ip = IP::new();
            {
                let mut ip = next_ip.build_schema::<value_string::Builder>();
                ip.set_value("next");
            }
            try!(self.ports.send("next", next_ip));
        }
        Ok(())
    }
}
