% This script shows several examples, demonstrating how to use solver pathfollow.
clear;
clc;

%% Simple LP 
% A = [1 1 -1  0;
%      1 2  0 -1];
A = [-1 -1 -1 1 0 0 0 0 1 0 0 0 0 0;
    0 0 0 -1 -1 -1 -1 0 0 1 0 0 1 0;
    1 0 0 0 1 0 0 0 0 0 1 0 0 0;
    0 1 0 0 0 1 0 1 0 0 0 0 0 0;
    0 0 1 0 0 0 1 -1 0 0 0 0 0 1;
    0 0 0 0 0 0 0 0 -1 -1 -1 -1 0 0];
% b = [ 3; 4];
b = [ 0; 0; 6; 10; 8; -9];
% c = [ 2; 1 ; 0; 0];
c = [ 53; 18; 29; 8; 60; 28; 37; 5; 44; 38; 98; 14; 23; 59];

p = pathfollow(A,b,c);
p.solve;


[xsol, fval, exitflag, iterations] = ...
    ipdipm(A, c, b, zeros(size(A,1), 1), -1, 0, ...
    100, 1e-08, 0.995, 6);

%% My approach
Anz = [-1 -1 -1 1 0 0 0 0 1 0 0 0 0;
    0 0 0 -1 -1 -1 -1 0 0 1 0 1 0;
    1 0 0 0 1 0 0 0 0 0 0 0 0;
    0 1 0 0 0 1 0 1 0 0 0 0 0;
    0 0 1 0 0 0 1 -1 0 0 0 0 1;
    0 0 0 0 0 0 0 0 -1 -1 -1 0 0];

Az = [0; 0; 1; 0; 0; -1];
% b = [ 3; 4];
b = [ 0; 0; 6; 10; 8; -9];
% c = [ 2; 1 ; 0; 0];
cnz = [ 53; 18; 29; 8; 60; 28; 37; 5; 44; 38; 14; 23; 59];
cz = [98];

p2 = PathFollowing(Az, Anz, b, cz, cnz);
p2.solve();


Anz = [-1 -1 1 0 0 0 1 0 0 0 0;
    0 0 -1 -1 -1 0 0 1 0 1 0;
    0 0 0 1 0 0 0 0 0 0 0;
    1 0 0 0 1 1 0 0 0 0 0;
    0 1 0 0 0 -1 0 0 0 0 1;
    0 0 0 0 0 0 -1 -1 -1 0 0];

Az = [-1 0 0; 
    0 -1 0; 
    1 0 1; 
    0 0 0; 
    0 1 0; 
    0 0 -1];

% b = [ 3; 4];
b = [ 0; 0; 6; 10; 8; -9];
% c = [ 2; 1 ; 0; 0];
cnz = [18; 29; 8; 60; 28; 5; 44; 38; 14; 23; 59];
cz = [53; 37; 98];

p3 = PathFollowing(Az, Anz, b, cz, cnz);
p3.solve();

%% Example on Randomly Generated Primal Nondegenrate LP
% This piece of code is from the book Linear Programming with Matalb
% m = 5;
% n = 8;
% 
% A = randn(m,n);
% 
% x = [rand(floor(n/2),1); zeros(n-floor(n/2),1)];
% s = [zeros(floor(n/2),1); rand(n-floor(n/2),1)];
% 
% x = x(randperm(n));
% s = s(randperm(n)); 
% 
% y = rand(m,1);
% 
% b = A*x; c=A'*y+s;
% 
% p = pathfollow(A,b,c);
% p.solve;

% %% Example from netlib (afiro)
% load lp_agg
% p = pathfollow(Problem.A,Problem.b,Problem.aux.c);
% p.solve;
