classdef LinearProgram < handle
    
    %% Properties
    properties
        Name;
        Az;
        Anz
        b;
        cz;
        cnz
        m;
        nz;
        nnz;
        optXz;
        optXnz
        optL;
        optS;
        optG;
        status;
    end
    
    %% Methods
    methods
        %% Constructor
        function lp = LinearProgram(Az, Anz, b, cz, cnz, Name)
            % Check needed arguments.
            if nargin < 6
                lp.Name = 'lp';
                if nargin < 5
                    error('LP: problem data (Az, Anz, b, cz, cnz) needed.');
                end
            else
                lp.Name = Name;
            end
            % Check dimensions.
            [tmp_m_z, tmp_n_z] = size(Az);
            [tmp_m_nz, tmp_n_nz] = size(Anz);
            if tmp_m_z ~= tmp_m_nz
                error('LP: Number of rows in Az and Anz must match.');
            end
            if tmp_n_z ~= size(cz, 1) || tmp_n_nz ~= size(cnz, 1)
                error('LP: Number of rows in cz (cnz) and number of columns in Az (Anz) must match.');
            end
            if tmp_m_z ~= size(b, 1)
                error('LP: Number of rows in b and Az (Anz) must match.');
            end
            if size(cz, 2) ~= 1 || size(cnz, 2) ~= 1 || size(b, 2) ~= 1
                error('LP: cz, cnz and b must be column vectors.');
            end
            lp.m = tmp_m_z;
            lp.nz = tmp_n_z;
            lp.nnz = tmp_n_nz;
            % Assign values to properties.
            if ~issparse(Az)
                lp.Az = sparse(Az);
            else
                lp.Az = Az;
            end
            if ~issparse(Anz)
                lp.Anz = sparse(Anz);
            else
                lp.Anz = Anz;
            end
            lp.b = b;
            lp.cz = cz;
            lp.cnz = cnz;
        end
        
        %% Setter functions
        function lp = setOptXz(lp, optXz)
            if size(optXz, 1) ~= lp.nz
                error('LP: cannot set xz - check the dimension.');
            else
                lp.optXz = optXz;
            end
        end
        
        function lp = setOptXnz(lp, optXnz)
            if size(optXnz, 1) ~= lp.nnz
                error('LP: cannot set xnz - check the dimension.');
            else
                lp.optXnz = optXnz;
            end
        end
        
        function lp = setOptL(lp, optL)
            if size(optL, 1) ~= lp.m
                error('LP: cannot set lambda - check the dimension.');
            else
                lp.optL = optL;
            end
        end
        
        function lp = setOptS(lp, optS)
            if size(optS, 1) ~= lp.nnz
                error('LP: cannot set s - check the dimension.');
            else
                lp.optS = optS;
            end
        end
        
        function lp = setOptG(lp, optG)
            if size(optG, 1) ~= lp.nz
                error('LP: cannot set gamma - check the dimension.');
            else
                lp.optG = optG;
            end
        end
        
        %% Get the objective function value
        function fval = getFval(lp)
            % getFval - get optimal objective function value
            fval = lp.cz' * lp.optXz + lp.cnz' * lp.optXnz;
        end
        
        %% Get A and c
        function A = getA(lp)
            A = [lp.Az, lp.Anz];
        end
        
        function c = getC(lp)
            c = [lp.cz; lp.cnz];
        end
    end
end