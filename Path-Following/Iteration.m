classdef Iteration < handle
   
    %% Properties
    properties (SetAccess = private)
        Rdz;
        Rdnz
        Rp;
        Rcz;
        Rcnz;
        residual;
        mu;
        
        xz;
        xnz;
        l;
        s;
        g;
        
        bc;
        
        alphaXz;
        alphaXnz;
        alphaL;
        alphaS;
        alphaG;
        
        k;
    end
    
    %% Methods
    methods
        %% Constructor
        function iter = Iteration(lp)
            iter.bc = 1 + max([norm(lp.b), norm(lp.cz), norm(lp.cnz)]);
            iter.k = 0;
        end
        
        %% Calculate residuals
        function calculateResiduals(iter, lp)
            iter.Rdz = lp.Az' * iter.l + iter.g - lp.cz;
            iter.Rdnz = lp.Anz' * iter.l + iter.s - lp.cnz;
            iter.Rp = lp.Az * iter.xz + lp.Anz * iter.xnz - lp.b;
            iter.Rcz = iter.xz .* iter.g;
            iter.Rcnz = iter.xnz .* iter.s;
            
            iter.mu = mean(iter.Rcnz);
            iter.residual = norm([iter.Rdz; iter.Rdnz; iter.Rp; iter.Rcz; iter.Rcnz]) / iter.bc;
        end
        
        %% Check termination conditions
        function termination = checkTermination(iter, lp, parameters)
            
            termination = 0;
            
            % Check residual.
            if ~isempty(iter.residual) && iter.residual < parameters.tol
                termination = 1;
                lp.status = 0;
            end
            
            % Check maxIter.
            if iter.k >= parameters.maxIter
                termination = 1;
                lp.status = 1;
            end
            
            % Set optimal solution.
            if termination 
                lp.setOptXz(iter.xz);
                lp.setOptXnz(iter.xnz);
                lp.setOptL(iter.l);
                lp.setOptS(iter.s);
                lp.setOptG(iter.g);
            end
        end
        
        %% Set up new iteration
        function nextIter(iter, newton)
            % Run this function after get Newton direction and step size.            
            iter.xz = iter.xz + iter.alphaXz * newton.dxz;
            iter.xnz = iter.xnz + iter.alphaXnz * newton.dxnz;
            iter.l = iter.l + iter.alphaL * newton.dl;
            iter.s = iter.s + iter.alphaS * newton.ds;
            iter.g = iter.g + iter.alphaG * newton.dg;                       
            
            iter.k = iter.k + 1;
        end
        
        %% Compute max step length
        function [alphaxz, alphaxnz, alphal, alphas, alphag] = stepLength(iter, params, newton)
            
            % Set the parameters eta defining fraction of max step to boundary
            eta = max(params.etaMin, 1 - iter.mu);
            
%             alphaxz = -1 / min(min(newton.dxz ./ iter.xz), -1);
            tmp = iter.xz ./ newton.dxz;
            alphaxz = min(1, min(-tmp(tmp < 0)));
            if isempty(alphaxz)
                alphaxz = 0;
            end
            iter.alphaXz = min(1, eta * alphaxz);
            
%             alphaxnz = -1 / min(min(newton.dxnz ./ iter.xnz), -1);
            tmp = iter.xnz ./ newton.dxnz;
            alphaxnz = min(1, min(-tmp(tmp < 0)));
            if isempty(alphaxnz)
                alphaxnz = 0;
            end
            iter.alphaXnz = min(1, eta * alphaxnz);
            
%             alphal = -1 / min(min(newton.dl ./ iter.l), -1);
            tmp = iter.l ./ newton.dl;
            alphal = min(1, min(-tmp(tmp < 0)));
            if isempty(alphal)
                alphal = 0;
            end
            iter.alphaL = min(1, eta * alphal);
            
%             alphas = -1 / min(min(newton.ds ./ iter.s), -1);
            tmp = iter.s ./ newton.ds;
            alphas = min(1, min(-tmp(tmp < 0)));
            if isempty(alphas)
                alphas = 0;
            end
            iter.alphaS = min(1, eta * alphas);
            
            tmp = iter.g ./ newton.dg;
            alphag = min(1, min(-tmp(tmp < 0)));
            if isempty(alphag)
                alphag = 0;
            end
            iter.alphaG = min(1, eta * alphag);
        end
                
        %% Get the starting point
        function initialPoint(iter, lp)
            % For reference, please refer to "On the Implementation of a Primal-Dual
            % Interior Point Method" by Sanjay Mehrotra.
            
            e = ones(lp.nz + lp.nnz, 1);
            A = lp.getA();
            c = lp.getC();
            
            % Solution for min norm(s) s.t. A'*l + s = c
            l0 = (A * A') \ (A * c);
            pi0 = c - A' * l0;
            
            % Solution for min norm(x) s.t. Ax = b
            x0 = A'* ((A * A') \ lp.b);
            
            % delta_x and delta_pi
            delta_x = max(-1.5 * min(x0), 0);
            delta_pi = max(-1.5 * min(pi0), 0);
            
            x0 = x0 + delta_x * e;
            pi0 = pi0 + delta_pi * e;
            
            % delta_x_c and delta_pi_c
            pdct = 0.5 * x0' * pi0;
            delta_x_c = pdct / sum(pi0);
            delta_pi_c = pdct / sum(x0);
            
            x0 = x0 + delta_x_c * e;
            pi0 = pi0 + delta_pi_c * e;
            
            iter.xz = x0(1:lp.nz);
            iter.xnz = x0(lp.nz + 1:end);
            iter.l = l0;
            iter.s = pi0(lp.nz + 1:end);
            iter.g = pi0(1:lp.nz);
        end
        
        %% Compute x and pi
        function x = getX(iter)
            x = [iter.xz; iter.xnz];
        end
        
        function pi = getPi(iter)
            pi = [iter.g; iter.s];
        end        
    end
end