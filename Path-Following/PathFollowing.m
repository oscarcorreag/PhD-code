classdef PathFollowing < handle
    
    %% Properties
    properties (SetAccess = private)
        lp;             % LP problem object
        params;     % Parameters object
        iter;           % Iteration object
        newton;         % Newton's direction object
        output;         % Output object        
    end
    
    %% Methods
    methods
        
        %% Constructor
        function p = PathFollowing(Az, Anz, b, cz, cnz, parameters)
            p.lp = LinearProgram(Az, Anz, b, cz, cnz);
            
            if nargin < 6
                p.params = Params;
            else
                p.params = Params(parameters);
            end
            
            p.iter = Iteration(p.lp);
            p.newton = NewtonDirection;
            p.output = Out;            
        end
        
        %% Main Solver         
        function solve(p)
            % Get initial point and it's residual
            p.iter.initialPoint(p.lp);
            p.iter.calculateResiduals(p.lp);
            
            % Main loop
            p.output.printHeader(p.lp, p.params)
            while ~p.iter.checkTermination(p.lp, p.params)
                
                % Output
                p.output.printIterations(p.iter, p.params)
                
                % Get Newton's dirction
                res = p.newton.predictorStep(p.iter, p.lp);
                if res
                    p.lp.setOptXz(p.iter.xz);
                    p.lp.setOptXnz(p.iter.xnz);
                    p.lp.setOptL(p.iter.l);
                    p.lp.setOptS(p.iter.s);
                    p.lp.setOptG(p.iter.g);
                    p.lp.status = 2;
                    break
                end
                
                % Get step length
                [~, alphaxnz, ~, alphas, ~] = p.iter.stepLength(p.params, p.newton) ;               
                
                % Get Newton's dirction
                p.newton.correctorStep(p.iter, alphaxnz, alphas, p.lp);
                
                % Update the iterate
                p.iter.nextIter(p.newton);
                
                % Calculate residuals
                p.iter.calculateResiduals(p.lp);
                                
            end % End while
            
            % Output the info of the final ipm iteration
            p.output.printIterations(p.iter, p.params);
            p.output.printFooter(p.lp, p.params);
        end
    end
end