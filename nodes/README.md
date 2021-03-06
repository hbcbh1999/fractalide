# Nodes collection

The `Nodes` collection consists of `Subgraphs` and `Agents`. A `Subgraph` or an `Agent` may be referred to as a `Node`.

## Subgraphs

### What?

A `Subgraph` consists of an implementation and an interface. The implementation is constructed using a simple language called `Flowscript` which describes how data flows through `Agents` and other `Subgraphs`. The interface aspect of a `Subgraph` consists of exposing a minimal set of well named `ports`, thus hiding complexity.

A simple analogy would be this gentleman's pocket watch.

![Image Alt](http://www.kirkwood.edu/pdf/uploaded/835/watchcalls_35.gif)

### Why?

Composition is an important part of programming, allowing one to hide implementation detail.

### Who?

People who want to focus on the Science tend to work at these higher abstractions, they'd prefer not getting caught up in the details of programming low level nodes and hand specifications to programmers who'll make efficient, reusable and safe `Agents`. Though programmers will find `Subgraphs` indispensable as they allow for powerful abstractions.

### Where?

The `Nodes` directory is where all `Agents` and `Subgraphs` go. Typically one might structure a hierarchy like such:

```
── wrangle
   ├── default.nix <------
   ├── aggregate
   ├── anonymize
   ├── print
   ├── processchunk
   │   ├── default.nix <------
   │   ├── agg_chunk_triples
   │   ├── convert_json_vector
   │   ├── extract_keyvalue
   │   ├── file_open
   │   └── iterate_paths
   └── stats
```

See the above `default.nix` files? Those are `Subgraphs` and they hide the entire directory level they reside in from higher levels in the hierarchy. Thus `processchunk` (a `Subgraph`) looks like yet another `Node` to `wrangle` (another `Subgraph`). Indeed `wrangle` is completely unable to distinguish between an `Agent` and a `Subgraph`.

### How?

The `Subgraph` `default.nix` requires you make decisions about two types of dependencies.
* What `Nodes` are needed?
* What `Edges` are needed?

Lastly:
* How to connect the lot to best solve your problem.

``` nix
{ subgraph, nodes, edges }:

subgraph {
 src = ./.;
 flowscript = with nodes; with edges; ''
  '${maths_boolean}:(boolean=true)' -> a nand(${maths_boolean_nand})
  '${maths_boolean}:(boolean=true)' -> b nand()
  nand() output -> input io_print(${maths_boolean_print})
 '';
}
```

![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex10.png)

* The `{ subgraph, nodes, edges }:` lambda passes in three arguments, the `subgraph` builder, `edges` which consists of every `Edge` or `Edge Namespace`, and the `nodes` argument which consists of every `Node` and `Node Namespace` in the system.
* The `subgraph` building function accepts these arguments:
  * The `src` attribute is used to derive a `Subgraph` name based on location in the directory hierarchy.
  * The `flowscript` attribute defines the business logic. Here data flowing through a system becomes a first class citizen that can be manipulated. `Nodes` and `Edges` are brought into scope between the opening '' and closing '' double single quotes by using the `with nodes; with edges;` syntax.
* `Nix` assists us greatly, in that each `node` name (the stuff between the curly quotes ``${...}``) undergoes a compilation step resolving every name into an absolute `/path/to/compiled/lib.subgraph` text file and `/path/to/compiled/libagent.so` shared object.
* This compilation is lazy and only referenced names will be compiled. In other words `Subgraph` could be a top level `Subgraph` of a many layer deep hierarchy and only referenced `Nodes` will be compiled in a lazy fashion, *not* the entire `fractalide/nodes` folder.

This is the output of the above `Subgraph`'s compilation:
```
$ cat /nix/store/1syrjhi6jvbvs5rvzcjn4z3qkabwss7m-test_sjm/lib/lib.subgraph
'/nix/store/fx46blm272yca7n3gdynwxgyqgw90pr5-maths_boolean:(boolean=true)' -> a nand(/nix/store/7yzx8fp81fl6ncawk2ag2nvfc5l950xb-maths_boolean_nand)
'/nix/store/fx46blm272yca7n3gdynwxgyqgw90pr5-maths_boolean:(boolean=true)' -> b nand()
nand() output -> input io_print(/nix/store/k67wiy6z4f1vnv35vdyzcqpwvp51j922-maths_boolean_print)
```

Mother of the Flying Spaghetti Monster, what is that? Those hashes hint at something powerful, projects like `docker` and `git` implement this type of content addressable store, except `docker`'s granularity is at container level, and `git`'s granularity is at every changeset. Our granularity is at package or library level. It allows for reproducible, deterministic systems, instead of copying around "zipped" archives, that quickly max out your hard drive.

### Flowscript syntax is easy

Everything between the opening `''` and closing `''` is `flowscript`, i.e:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
                       <---- here
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex0.png)


#### Agent initialization:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    agent_name(${name_of_agent})
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex1.png)

#### Referencing a previously initialized agent (with a comment):
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    agent_name(${name_of_agent}) // <──┐
    agent_name()                 // <──┴─ same instance
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex1.png)

#### Connecting and initializing two agents:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    agent1(${name_of_agent1}) output_port -> input_port agent2(${name_of_agent2})
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex3.png)

#### Creating an Initial Information Packet
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    '${maths_boolean}:(boolean=true)' -> a agent(${name_of_agent})
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex4.png)

#### More complex Initial Information Packet
``` nix
{ subgraph, edges, nodes }:

subgraph {
  src = ./.;
  flowscript = with edges; with nodes; ''
   td(${ui_js_nodes.flex})
   '${js_create}:(type="div", style=[(key="display", val="flex"), (key="flex-direction", val="column")])~create' -> input td()
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex5.png)

[Learn](../edges/README.md) more about Information Packets.
#### Creating an subgraph input port
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    subgraph_input => input agent(${name_of_agent})
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex6.png)

#### Creating an subgraph output port
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
     agent(${name_of_agent}) output => subgraph_output
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex7.png)

#### Subgraph initialization:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    subgraph(${name_of_subgraph})
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex8.png)

#### Initializing a subgraph and agent then connecting them:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    subgraph(${name_of_subgraph})
    agent(${name_of_agent})
    subgraph() output -> input agent()
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex9.png)

#### Output array port:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    db_path => input clone(${ip_clone})
    clone() clone[0] => db_path0
    clone() clone[1] => db_path1
    clone() clone[2] => db_path2
    clone() clone[3] => db_path3
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex11.png)

Note the `clone[1]`, this is an `array output port` and in this particular `Subgraph` `Information Packets` are being replicated, a copy for each port element. The content between the `[` and `]` is a string, so don't be misled by the integers. There are two types of node ports, a `simple port` (which doesn't have array elements) and an `array port` (with array elements). The `array port` allows one to, depending on node logic, replicate, fan-out and a whole bunch of other things.

#### Input array port:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    add0 => add[0] adder(${path_to_adder})
    add1 => add[1] adder()
    add2 => add[2] adder()
    add3 => add[3] adder() output -> output
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex15.png)

`Array ports` are used when the number of ports are unknown at `Agent` development time, but known when the `Agent` is used in a `Subgraph`. The `adder` `Agent` demonstrates this well, it has an `array input port` which allows `Subgraph` developers to choose how many integers they want to add together. It really doesn't make sense to implement an adder with two simple input ports then be constrained when you need to add three numbers together.

#### Hierarchical naming:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    input => input clone(${ip_clone})
    clone() clone[0] -> a nand(${maths_boolean_nand})
    clone() clone[1] -> b nand() output => output
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex13.png)

The `Node` and `Edge` names, i.e.: `${maths_boolean_nand}` are too long! Fractalide uses a hierarchical naming scheme. So you can find the `maths_boolean_not` node by going to the [maths/boolean/not](./maths/boolean/not/default.nix) directory. The whole goal of this is to avoid name shadowing among potentially hundreds to thousands of nodes.

Explanation of the `Subgraph`:

This `Subgraph` takes an input of `Edge` type [maths_boolean](../edges/maths/boolean/default.nix) over the `input` port. The `Information Packet` is cloned by the `clone` node and the result is pushed out on the `array output port` `clone` using elements `[0]` and `[1]`. The `nand()` node then performs a `NAND` boolean logic operation and outputs a `maths_boolean` data type, which is then sent over the `Subgraph` output port `output`.

The above implements the `not` boolean logic node.

#### Abstraction powers:
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    '${maths_boolean}:(boolean=true)' -> a nand(${maths_boolean_nand})
    '${maths_boolean}:(boolean=true)' -> b nand()
    nand() output -> input not(${maths_boolean_not})
    not() output -> input print(${maths_boolean_print})
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex14.png)

Notice we're using the `not` node implemented earlier. One can build hierarchies many layers deep without suffering a run-time performance penalty. Once the graph is loaded into memory, all `Subgraphs` fall away, like water, after an artificial gravity generator engages, leaving only `Agents` connected to `Agents`.

#### Namespaces
``` nix
{ subgraph, nodes, edges }:

subgraph {
  src = ./.;
  flowscript = with nodes; with edges; ''
    listen => listen http(${net_http_nodes.http})
    db_path => input clone(${ip_clone})
    clone() clone[1] -> db_path get(${app_todo_nodes.todo_get})
    clone() clone[2] -> db_path post(${app_todo_nodes.todo_post})
    clone() clone[3] -> db_path del(${app_todo_nodes.todo_delete})
    clone() clone[4] -> db_path patch(${app_todo_nodes.todo_patch})

    http() GET[/todos/.+] -> input get() response -> response http()
    http() POST[/todos/?] -> input post() response -> response http()
    http() DELETE[/todos/.+] -> input del() response -> response http()
    http() PATCH[/todos/.+] -> input patch()
    http() PUT[/todos/.+] -> input patch() response -> response http()
  '';
}
```
![Image Alt](https://raw.githubusercontent.com/fractalide/fractalide/master/doc/images/subnet_ex12.png)

Notice the `net_http_nodes` and `app_todo_nodes` namespaces. Some [fractals](../fractals/README.md) deliberately export a collection of `Nodes`. As is the case with the `net_http_nodes.http` node.
When you see a `fullstop` `.`, i.e. `xxx_nodes.yyy` you immediately know this is a namespace. It's also a programming convention to use the `_nodes` suffix.
Lastly, notice the advanced usage of `array ports` with this example: `GET[/todos/.+]`, the element label is actually a `regular expression` and the implementation of that node is slightly more [advanced](https://github.com/fractalide/fractal_net_http/blob/master/nodes/http/src/lib.rs#L149)!



## Agents

### What?

Executable `Subgraphs` are defined as a network of `Agents`, which exchange typed data across predefined connections by message passing, where the connections are specified externally to the processes. These `Agents`  can be reconnected endlessly to form different executable `Subgraphs` without having to be changed internally.

### Why?

Functions in a programming language should be placed in a content addressable store, this is the horizontal plane. The vertical plane should be constructed using unique addresses into this content addressable store, critically each address should solve a single problem, and may do so by referencing multiple other unique addresses in the content addressable store. Users must not have knowledge of these unique addresses but a translation process should occur from a human readable name to a universally unique address. Read [more](http://erlang.org/pipermail/erlang-questions/2011-May/058768.html) about the problem.

Once you have the above, you have truly reusable functions. Fractalide nodes are just this, and it makes the below so much easier to achieve:
```
* Open source collaboration
* Open Peer review of nodes
* Nice clean reusable nodes
* Reproducible applications
```

### Who?

Typically programmers will develop `Agents`. They specialize in making `Agents` as efficient and reusable as possible, while people who focus on the Science give the requirements and use the `Subgraphs`. Just as a hammer is designed to be reused, so `Subgraphs` and `Agents` should be designed for reuse.

### Where?

The `Agents` are found in this `nodes` directory, or the `nodes` directory of a [fractal](../fractals/README.md).

```
processchunk
├── default.nix
├── agg_chunk_triples
│   ├── default.nix <---
│   └── lib.rs
├── convert_json_vector
│   ├── default.nix <---
│   └── lib.rs
├── extract_keyvalue
│   ├── default.nix <---
│   └── lib.rs
├── file_open
│   ├── default.nix <---
│   └── lib.rs
└── iterate_paths
    ├── default.nix <---
    └── lib.rs
```
Typically when you see a `lib.rs` in the same directory as a `default.nix` you know it's an `Agent`.

### How?

The `Agent` `default.nix` requires you make decisions about three types of dependencies.
* What `edges` are needed?
* What `crates` from [crates.io](https://crates.io) are needed?
* What `osdeps` or `operating system level dependencies` are needed?

In all the above cases transitive dependencies are resolved for you.

``` nix
{ agent, edges, crates, pkgs }:

let
  rustfbp = crates.rustfbp { vsn = "0.3.21"; };
  capnp = crates.capnp { vsn = "0.7.4"; };
in
agent {
  src = ./.;
  edges = with edges; [ maths_boolean ];
  crates = [ rustfbp capnp ];
  osdeps = with pkgs; [ openssl ];
}
```

The `{ agent, edges, crates, pkgs }:` lambda imports:
* The `agent` function builds the rust `lib.rs` source code in the same directory.
* The `edges` attribute set consists of every `edge` available on the system.
* The `crates` attribute set consists of every `crate` on https://crates.io.
* The `pkgs` pulls in every third party package available on NixOS, here's the whole [list](http://nixos.org/nixos/packages.html).
Note only those dependencies and their transitive dependencies will be pulled into scope and compiled, if their binaries aren't available. So you get a source distribution with a binary distribution optimization.

What does the output of the `agent` that builds the `maths_boolean_nand` node look like?

```
/nix/store/dp8s7d3p80q18a3pf2b4dk0bi4f856f8-maths_boolean_nand
└── lib
    └── libagent.so
```
