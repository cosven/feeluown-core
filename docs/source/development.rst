Development
===========

Quickstart
----------

Architecture
------------

.. graphviz::

   digraph "all" {
     rankdir=BT

     subgraph cluster3 {
       rankdir=LR
       label = "Kernel";
       player [label="player: mpv"];
       model;
       source;

       source -> model [label="serialize"];
       model -> player [label="song"];
     }
     subgraph cluster1 {
       protocol;
     }

     subgraph cluster2 {
       label = "User Interface";
       emacs_fuo [label="Emacs Client"];
       GUI [label="GUI: feeluown" style="dashed"];
       CLI [label="CLI: fuocli"];
     }

     subgraph cluster0 {
       label="Plugins"
       netease [label="provider: netease"];
       qq [label="provider: qq"]
       xiami [label="provider: xiami"];
       local [label="provider: local"];
     }

     qq -> source [style="dotted"];
     netease -> source;
     xiami -> source [style="dotted"];
     local -> source [style="dotted"];

     source -> protocol;
     player -> protocol;

     protocol -> GUI;
     protocol -> CLI;
     protocol -> emacs_fuo;
   }


Code Structure
--------------

.. code::

    fuocore
    ├── core  # modules will be reused by other programs
    ├── daemon  # fuo dependency
    ├── local  # a provider example
    ├── netease  # a provider example
    ├── protocol  # fuo protocol related
    ├── xxx.py  # private modules which used by fuo itself or plugins
    └── xiami  # a provider example

Code Style
----------

Log
"""
- each log entry should start with uppercase letter.

Comments
""""""""
- comment with ``NOTE`` flag indicate that it is a basic theory
  or something that is considered as best practice.
