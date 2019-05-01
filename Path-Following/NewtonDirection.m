classdef NewtonDirection < handle
    %% Properties
    properties (SetAccess = private)
        sigma; 
        dxz;
        dxnz;
        dl;
        ds;
        dg;
        
        R;
        
        L;
        D;
        pm;
    end
    
    %% Methods
    methods
        %% Constructor
        function newton = NewtonDirection()
        end
        
        %% Predictor step
        function res = predictorStep(newton, iter, lp)        
            A = lp.getA();
            x = iter.getX();
            pi = iter.getPi();
            M = A * diag(x ./ pi) * A';
            [newton.R, p] = chol(M); % factorize M
%             [newton.L, newton.D, newton.pm] = ldl(M, 'vector');
            if p > 0
                disp('AD^2A^T is symmetric positive definite');
                res = 1;
                return
            end
            Rxs = [iter.Rcz; iter.Rcnz];
            Rd = [iter.Rdz; iter.Rdnz];
            rhs = -iter.Rp + A * ((Rxs - x .* Rd) ./ pi);
            % Compute Newton direction to solve the original system.
%             d = zeros(prob.m + prob.n, 1);
%             newton.dl(newton.pm, :) = newton.L'\(newton.D\(newton.L\(rhs(newton.pm, :))));
            newton.dl = newton.R \ (newton.R' \ rhs);
            dpi = -Rd - A' * newton.dl;
            newton.ds = dpi(lp.nz + 1:end);
            newton.dg = dpi(1:lp.nz);
            dx = (-Rxs - x .* dpi) ./ pi;
            newton.dxz = dx(1:lp.nz);
            newton.dxnz = dx(lp.nz + 1:end);
            res = 0;
        end
        
        %% Corrector step
        function correctorStep(newton, iter, alphaxnz, alphas, lp)
            % centering parameter step
            mun = ((iter.xnz + alphaxnz * newton.dxnz)' * (iter.s + alphas * newton.ds)) / lp.nnz;
            newton.sigma = (mun / iter.mu) ^ 3;
            % corrector step
            A = lp.getA();
            x = iter.getX();
            pi = iter.getPi();
            Rd = [iter.Rdz; iter.Rdnz];
            DD = diag(x ./ pi);
%             corz = newton.dxz .* newton.dg;
%             cornz = newton.dxnz .* newton.ds;
            corz = zeros(lp.nz, 1);
            cornz = zeros(lp.nnz, 1);
            rhs = -iter.Rp - A * DD * Rd - A * diag(1 ./ pi) * [-iter.Rcz; newton.sigma * iter.mu - iter.Rcnz] + A * DD * diag(1 ./ x) * [corz; cornz];
            
%             Rxs = [Rxg; Ru];            
%             rhs = -iter.Rp + A * ((-Rxs - x .* Rd) ./ pi);

            Rxg = -iter.xz .* iter.g - newton.dxz .* newton.dg;
            Ru = newton.sigma * iter.mu - iter.xnz .* iter.s - newton.dxnz .* newton.ds;            
            
            newton.dl = newton.R \ (newton.R' \ rhs);
            
%             newton.dl(newton.pm, :) = newton.L'\(newton.D\(newton.L\(rhs(newton.pm, :))));
            
            newton.ds = -iter.Rdnz - lp.Anz' * newton.dl;
            newton.dg = -iter.Rdz - lp.Az' * newton.dl;
            newton.dxz = (Rxg - iter.xz .* newton.dg) ./ iter.g;
            newton.dxnz = (Ru - iter.xnz .* newton.ds) ./ iter.s;
        end
    end
end